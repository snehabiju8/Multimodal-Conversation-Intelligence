from __future__ import annotations

import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.security import verify_api_key
from app.models.schemas import AnalyzeTextRequest, ClientConfig
from app.services.analysis_service import AnalysisService

router = APIRouter(tags=["v1"])


@router.get("/health", tags=["health"])
def health():
    return {"status": "ok"}


def load_config_from_json_str(config_json: str | None) -> ClientConfig:
    if not config_json:
        return ClientConfig()
    try:
        data = json.loads(config_json)
        return ClientConfig.model_validate(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid config JSON: {e}")


@router.post("/analyze", dependencies=[Depends(verify_api_key)])
async def analyze(
    # JSON text mode (body)
    body: AnalyzeTextRequest | None = None,
    # Multipart audio mode
    audio: UploadFile | None = File(default=None),
    config: str | None = Form(default=None),
):
    """
    Analyze either:
    - JSON body: { "input_type": "text", "transcript": "...", "config": {...} }
    - multipart/form-data: audio=<file>, config="<json string>"
    """
    service = AnalysisService()

    # If multipart audio was provided, prioritize it
    if audio is not None:
        if audio.size is not None:
            max_bytes = settings.max_audio_mb * 1024 * 1024
            if audio.size > max_bytes:
                raise HTTPException(status_code=413, detail=f"Audio too large. Max {settings.max_audio_mb}MB")

        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file")

        cfg = load_config_from_json_str(config)
        mime_type = audio.content_type or "audio/wav"

        parsed = service.analyze_audio(audio_bytes=audio_bytes, mime_type=mime_type, cfg=cfg)
        resp = service.to_api_response(
            parsed=parsed,
            input_meta={"type": "audio", "mime_type": mime_type, "filename": audio.filename},
            cfg=cfg,
        )
        return JSONResponse(content=resp)

    # Otherwise require JSON text body
    if body is None:
        raise HTTPException(status_code=400, detail="Provide either JSON body with transcript or multipart audio upload.")

    cfg = body.config or ClientConfig()
    parsed = service.analyze_transcript(transcript=body.transcript, cfg=cfg)
    resp = service.to_api_response(
        parsed=parsed,
        input_meta={"type": "text"},
        cfg=cfg,
    )
    return JSONResponse(content=resp)