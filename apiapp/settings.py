# apiapp/settings.py
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices

class APISettings(BaseSettings):
    app_name: str = "FastAPI x Django Demo"
    debug: bool = False

    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = None
    aws_s3_bucket: Optional[str] = None

    runpod_api_key: Optional[str] = None
    runpod_endpoint: Optional[str] = None

    hf_token: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("HF_TOKEN", "hf_token")
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = APISettings()
