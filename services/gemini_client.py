from __future__ import annotations

from app.core.config import settings

try:
    from google import genai
except Exception as e:  # pragma: no cover
    genai = None


class GeminiClient:
    def __init__(self):
        if genai is None:
            raise RuntimeError(
                "google-genai is not installed. Add it to requirements.txt: google-genai"
            )
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is missing. Set it in environment or .env file.")

        self.client = genai.Client(api_key=settings.gemini_api_key)

    def generate_text(self, prompt: str, model: str | None = None) -> str:
        mdl = model or settings.gemini_model_text
        resp = self.client.models.generate_content(
            model=mdl,
            contents=prompt,
        )
        return (resp.text or "").strip()

    def generate_multimodal_audio(self, prompt: str, audio_bytes: bytes, mime_type: str) -> str:
        """
        Attempts audio+text multimodal analysis. If your Gemini model/account doesn't support audio,
        switch to an STT fallback approach.
        """
        mdl = settings.gemini_model_multimodal

        # google-genai supports content "parts"
        resp = self.client.models.generate_content(
            model=mdl,
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": mime_type, "data": audio_bytes}},
                    ],
                }
            ],
        )
        return (resp.text or "").strip()