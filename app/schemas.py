from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


RiskBand = Literal["low", "medium", "high"]
Direction = Literal["increases_risk", "decreases_risk", "neutral"]


class FhirBundleRequest(BaseModel):
    """Typed wrapper for API clients that prefer an explicit request object."""

    model_config = ConfigDict(json_schema_extra={"examples": [{"bundle": {"resourceType": "Bundle", "entry": []}}]})

    bundle: dict[str, Any] = Field(..., description="FHIR-style Bundle JSON object.")

    @field_validator("bundle")
    @classmethod
    def validate_bundle(cls, value: dict[str, Any]) -> dict[str, Any]:
        if value.get("resourceType") != "Bundle":
            raise ValueError("bundle.resourceType must be 'Bundle'")
        if not isinstance(value.get("entry", []), list):
            raise ValueError("bundle.entry must be a list when provided")
        return value


class BatchScoreRequest(BaseModel):
    bundles: list[dict[str, Any]] = Field(..., min_length=1, max_length=50)

    @field_validator("bundles")
    @classmethod
    def validate_bundles(cls, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for bundle in value:
            if bundle.get("resourceType") != "Bundle":
                raise ValueError("each item must be a FHIR-style Bundle")
        return value


class TopFeature(BaseModel):
    feature: str
    value: float | int | str
    direction: Direction


class ScoreResponse(BaseModel):
    patient_id: str
    model_version: str
    readmission_risk_probability: float = Field(..., ge=0.0, le=1.0)
    risk_band: RiskBand
    top_features: list[TopFeature]
    data_notice: str


class BatchScoreResponse(BaseModel):
    model_version: str
    results: list[ScoreResponse]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_version: str
    data_notice: str


class ModelCardResponse(BaseModel):
    model_version: str
    intended_use: str
    limitations: list[str]
    feature_groups: list[str]
    data_notice: str

