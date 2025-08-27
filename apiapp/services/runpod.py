# apiapp/services/runpod.py
from typing import Optional
import httpx

class RunpodClient:
    def __init__(self, api_key: Optional[str], endpoint: Optional[str]):
        self.api_key = api_key
        self.endpoint = endpoint
        self.enabled = bool(api_key and endpoint)

    async def infer_echo(self, payload: dict) -> dict:
        if not self.enabled:
            return {"status": "DRY-RUN", "echo": payload}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(self.endpoint, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()
