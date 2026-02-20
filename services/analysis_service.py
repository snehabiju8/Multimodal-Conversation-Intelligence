from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.models.schemas import ClientConfig, FlagItem
from app.services.gemini_client import GeminiClient


SYSTEM_INSTRUCTIONS = """You are an enterprise conversation intelligence engine.
Return ONLY valid JSON. Do not wrap in markdown. Do not include extra keys not asked.
If unsure, return best-effort with empty arrays/strings, never non-JSON text.
"""


def build_prompt(transcript: str, cfg: ClientConfig) -> str:
    # Keep prompt explicit and schema-locked to avoid hallucinated formats
    schema = {
        "detected_languages": ["string"],
        "summary": "string",
        "sentiment": {
            "label": "positive|neutral|negative|mixed",
            "emotional_tone": ["string"],
            "rationale": "string",
        },
        "intents": [{"intent": "string", "confidence": 0.0}],
        "topics_entities": {
            "topics": [{"topic": "string", "confidence": 0.0}],
            "entities": [{"text": "string", "type": "PERSON|ORG|PRODUCT|LOCATION|ACCOUNT|OTHER"}],
        },
        "advanced": {
            "compliance": {
                "violations": [
                    {
                        "policy": "string",
                        "severity": "low|medium|high",
                        "description": "string",
                        "evidence_quotes": ["string"],
                        "triggers": ["string"],
                    }
                ]
            },
            "outcome": {
                "label": "resolved|escalated|dropped|follow_up_needed|unknown",
                "confidence": 0.0,
                "rationale": "string",
            },
            "risk_score": {
                "score": 0,
                "level": "low|medium|high",
                "rationale": "string",
            },
        },
        "debug": {
            "assumptions": ["string"],
        },
    }

    return f"""{SYSTEM_INSTRUCTIONS}

Client context:
- domain: {cfg.domain}
- products: {cfg.products}
- policies: {cfg.policies}
- risk_triggers: {cfg.risk_triggers}

Task:
Analyze the conversation transcript and produce structured conversation intelligence.
You MUST:
1) Auto-detect languages present.
2) Summarize the conversation.
3) Assess sentiment/emotional tone.
4) Identify primary intents with confidence (0 to 1).
5) Extract key topics and named entities.
6) Perform advanced analysis:
   - Compliance/policy violation detection using policies and risk_triggers.
   - Outcome classification.
   - Risk score from 0-100 with level.

Output JSON schema (example types only):
{json.dumps(schema, ensure_ascii=False)}

Transcript:
{transcript}
"""


def safe_json_loads(text: str) -> dict[str, Any]:
    """
    Tries to parse strict JSON. If model returns stray text, attempts to extract JSON object.
    """
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # crude extraction: find first { and last }
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


class AnalysisService:
    def __init__(self):
        self.client = GeminiClient()

    def analyze_transcript(self, transcript: str, cfg: ClientConfig) -> dict[str, Any]:
        prompt = build_prompt(transcript, cfg)
        raw = self.client.generate_text(prompt)
        parsed = safe_json_loads(raw)
        return parsed

    def analyze_audio(self, audio_bytes: bytes, mime_type: str, cfg: ClientConfig) -> dict[str, Any]:
        # We ask Gemini to both understand audio and generate the same JSON schema
        prompt = build_prompt(
            transcript=(
                "The user provided an AUDIO conversation. "
                "Transcribe internally as needed and perform the analysis on the conversation content."
            ),
            cfg=cfg,
        )
        raw = self.client.generate_multimodal_audio(prompt=prompt, audio_bytes=audio_bytes, mime_type=mime_type)
        parsed = safe_json_loads(raw)
        return parsed

    @staticmethod
    def to_api_response(parsed: dict[str, Any], input_meta: dict[str, Any], cfg: ClientConfig) -> dict[str, Any]:
        request_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        # Convert violations to top-level flags as well
        flags: list[FlagItem] = []
        violations = (((parsed.get("advanced") or {}).get("compliance") or {}).get("violations") or [])
        for v in violations:
            flags.append(
                FlagItem(
                    type="compliance_violation",
                    severity=v.get("severity", "medium"),
                    description=v.get("description", ""),
                    policy=v.get("policy"),
                    triggers=v.get("triggers") or [],
                    evidence=[{"text": q} for q in (v.get("evidence_quotes") or [])],
                )
            )

        out_opts = cfg.output_options
        insights: dict[str, Any] = {}
        advanced: dict[str, Any] = {}

        if out_opts.get("language", True):
            insights["detected_languages"] = parsed.get("detected_languages", [])
        if out_opts.get("summary", True):
            insights["summary"] = parsed.get("summary", "")
        if out_opts.get("sentiment", True):
            insights["sentiment"] = parsed.get("sentiment", {})
        if out_opts.get("intents", True):
            insights["intents"] = parsed.get("intents", [])
        if out_opts.get("topics_entities", True):
            insights["topics_entities"] = parsed.get("topics_entities", {})

        if out_opts.get("compliance", True) or out_opts.get("outcome", True) or out_opts.get("risk_score", True):
            adv = parsed.get("advanced", {}) or {}
            if out_opts.get("compliance", True):
                advanced["compliance"] = adv.get("compliance", {})
            if out_opts.get("outcome", True):
                advanced["outcome"] = adv.get("outcome", {})
            if out_opts.get("risk_score", True):
                advanced["risk_score"] = adv.get("risk_score", {})

        resp = {
            "request_id": request_id,
            "input": {
                **input_meta,
                "received_at": now,
                "domain": cfg.domain,
            },
            "insights": insights,
            "advanced": advanced,
            "flags": [f.model_dump() for f in flags],
        }

        if out_opts.get("debug", False):
            resp["debug"] = {
                "model_raw_keys": list(parsed.keys()),
                "debug": parsed.get("debug", {}),
            }

        return resp