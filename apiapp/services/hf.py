from typing import Optional, List
import httpx
from apiapp.settings import settings

_DEFAULT_MODELS: List[str] = [
    "distilbert-base-uncased-finetuned-sst-2-english",
    "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "nlptown/bert-base-multilingual-uncased-sentiment",
    "finiteautomata/bertweet-base-sentiment-analysis",
]

class HuggingFaceClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.hf_token
        self.base = "https://api-inference.huggingface.co/models"
        self.headers = {
            **({"Authorization": f"Bearer {self.token}"} if self.token else {}),
            "x-wait-for-model": "true",  # helps with cold starts
        }

    async def sentiment(self, text: str) -> dict:
        if not self.token:
            # Keep demo working without any cloud creds
            return {"status": "DRY-RUN", "echo": text}

        payload = {"inputs": text}
        last_error = None
        async with httpx.AsyncClient(timeout=60) as client:
            for model in _DEFAULT_MODELS:
                url = f"{self.base}/{model}"
                r = await client.post(url, headers=self.headers, json=payload)
                if r.status_code == 200:
                    return {"model": model, "result": r.json()}
                if r.status_code in (401, 403):
                    return {
                        "error": "Unauthorized/Forbidden",
                        "hint": "Check HF_TOKEN in .env and token scopes.",
                        "status": r.status_code,
                        "model": model,
                        "body": r.text,
                    }
                # collect and try next model (handles 404/5xx)
                last_error = {"status": r.status_code, "model": model, "body": r.text}

        return {
            "error": "All sentiment models failed",
            "hint": "Model may be warming or temporarily unavailable.",
            "last_error": last_error,
        }
