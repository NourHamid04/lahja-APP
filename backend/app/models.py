from typing import Literal
from pydantic import BaseModel, Field, field_validator

from app.config import get_settings
from app.dialects import DIALECT_IDS

ScriptType = Literal["auto", "arabic", "arabizi", "mixed"]
OutputScript = Literal["arabic", "arabizi"]
Tone = Literal["neutral", "casual", "friendly", "formal"]


class TransformRequest(BaseModel):
    text: str = Field(..., min_length=1)
    source_dialect: str = "auto"
    target_dialect: str
    input_script: ScriptType = "auto"
    output_script: OutputScript = "arabic"
    tone: Tone = "neutral"
    preserve_names: bool = True

    @field_validator("text")
    @classmethod
    def validate_text_length(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("Text cannot be empty.")
        if len(text) > get_settings().max_text_length:
            raise ValueError(f"Text is longer than {get_settings().max_text_length} characters.")
        return text

    @field_validator("source_dialect")
    @classmethod
    def validate_source(cls, value: str) -> str:
        if value not in DIALECT_IDS:
            raise ValueError("Unsupported source dialect.")
        return value

    @field_validator("target_dialect")
    @classmethod
    def validate_target(cls, value: str) -> str:
        if value == "auto" or value not in DIALECT_IDS:
            raise ValueError("Choose a supported target dialect.")
        return value


class AITransformResult(BaseModel):
    transformed_text: str
    detected_source_dialect: str
    detected_input_script: Literal["arabic", "arabizi", "mixed", "unknown"]
    confidence: float = Field(ge=0, le=1)
    notes: list[str] = Field(default_factory=list, max_length=4)
    alternatives: list[str] = Field(default_factory=list, max_length=3)
    warnings: list[str] = Field(default_factory=list, max_length=4)


class TransformResponse(AITransformResult):
    request_id: str
    model: str
    latency_ms: int
    mock_mode: bool = False


class HealthResponse(BaseModel):
    status: str
    version: str
    model: str
    mock_mode: bool
