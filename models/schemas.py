from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class ClientConfig(BaseModel):
    domain: str = Field(default="general", description="Business domain (banking/telecom/support/etc.)")
    products: list[str] = Field(default_factory=list)
    policies: list[str] = Field(default_factory=list, description="Policy or compliance rules in plain language")
    risk_triggers: list[str] = Field(default_factory=list, description="Keywords/phrases or triggers to flag")
    output_options: dict[str, bool] = Field(
        default_factory=lambda: {
            "summary": True,
            "language": True,
            "sentiment": True,
            "intents": True,
            "topics_entities": True,
            "compliance": True,
            "outcome": True,
            "risk_score": True,
            "debug": False,
        }
    )


class AnalyzeTextRequest(BaseModel):
    input_type: Literal["text"] = "text"
    transcript: str = Field(min_length=1)
    config: ClientConfig | None = None


class EvidenceItem(BaseModel):
    text: str
    speaker: str | None = None
    timestamp: str | None = None


class FlagItem(BaseModel):
    type: str
    severity: Literal["low", "medium", "high"]
    description: str
    policy: str | None = None
    triggers: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    request_id: str
    input: dict[str, Any]
    insights: dict[str, Any]
    advanced: dict[str, Any]
    flags: list[FlagItem] = Field(default_factory=list)
    debug: dict[str, Any] | None = None