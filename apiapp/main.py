from typing import List, Optional
import asyncio, time, concurrent.futures
from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import requests
import httpx

from apiapp.models import UserCreate, UserOut, Item
from apiapp.deps import get_db, FakeDB
from apiapp.settings import settings
from apiapp.services.s3 import S3Client
from apiapp.services.runpod import RunpodClient
from apiapp.services.hf import HuggingFaceClient

app = FastAPI(title=settings.app_name)

from anyio.to_thread import current_default_thread_limiter

@app.on_event("startup")
async def cap_threadpools() -> None:
    loop = asyncio.get_running_loop()
    loop.set_default_executor(concurrent.futures.ThreadPoolExecutor(max_workers=1))
    current_default_thread_limiter().total_tokens = 1
    print(">> capped threadpools: asyncio=1, anyio=1")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

s3 = S3Client(
    access_key=settings.aws_access_key_id,
    secret_key=settings.aws_secret_access_key,
    region=settings.aws_region,
)
runpod = RunpodClient(settings.runpod_api_key, settings.runpod_endpoint)
hf = HuggingFaceClient()

requests_session: Optional[requests.Session] = None
async_client: Optional[httpx.AsyncClient] = None

@app.on_event("startup")
async def startup_clients() -> None:
    global requests_session, async_client
    requests_session = requests.Session()
    async_client = httpx.AsyncClient(timeout=10)

@app.on_event("shutdown")
async def shutdown_clients() -> None:
    global requests_session, async_client
    if requests_session:
        requests_session.close()
        requests_session = None
    if async_client:
        await async_client.aclose()
        async_client = None

@app.get("/health")
def health():
    return {"ok": True, "app": settings.app_name}

@app.post("/users", response_model=UserOut, status_code=201)
async def create_user(payload: UserCreate, db: FakeDB = Depends(get_db)) -> UserOut:
    user = db.add_user(payload.model_dump())
    return UserOut(**user)

@app.get("/users", response_model=List[UserOut])
async def list_users(db: FakeDB = Depends(get_db)) -> List[UserOut]:
    return [UserOut(**u) for u in db.list_users()]

@app.get("/sync-slow")
def sync_slow():
    time.sleep(2)
    return {"kind": "sync", "slept": 2}

@app.get("/async-slow")
async def async_slow():
    await asyncio.sleep(2)
    return {"kind": "async", "slept": 2}

def _log_to_s3(message: str) -> None:
    if settings.aws_s3_bucket:
        s3.upload_text(settings.aws_s3_bucket, "logs/app.log", message + "\n")

@app.post("/background")
async def run_background(tasks: BackgroundTasks, msg: str = "hello"):
    tasks.add_task(_log_to_s3, f"BG: {msg}")
    return {"enqueued": True}

@app.post("/runpod/echo", operation_id="runpod_echo_v1")
async def runpod_echo(payload: dict) -> dict:
    return await runpod.infer_echo(payload)

@app.post("/huggingface/sentiment", operation_id="hf_sentiment_v1")
async def sentiment_analysis(payload: dict):
    text = payload.get("text", "")
    return await hf.sentiment(text)

@app.get("/fake-remote")
async def fake_remote(delay: float = 2.0):
    await asyncio.sleep(delay)
    return {"ok": True, "delay": delay}

from fastapi.responses import JSONResponse
from starlette import status as http_status

@app.get("/sync-http")
def sync_http():
    try:
        assert requests_session is not None
        r = requests_session.get("https://httpbin.org/delay/2", timeout=10)
        return {"ok": True, "status": r.status_code}
    except Exception as e:
        return JSONResponse(
            {"ok": False, "error": str(e)},
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
        )

@app.get("/async-http")
async def async_http():
    try:
        assert async_client is not None
        r = await async_client.get("https://httpbin.org/delay/2")
        return {"ok": True, "status": r.status_code}
    except Exception as e:
        return JSONResponse(
            {"ok": False, "error": str(e)},
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
        )
