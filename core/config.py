from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_model_text: str = "gemini-1.5-flash"
    gemini_model_multimodal: str = "gemini-1.5-flash"

    # Optional simple auth (bonus)
    api_key_required: bool = False
    api_key: str = ""

    # Safety / limits
    max_audio_mb: int = 25
    request_timeout_seconds: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()