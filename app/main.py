from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

from app.explainability import top_features
from app.features import build_features
from app.fhir_parser import patient_id
from app.model import DATA_NOTICE, MODEL_VERSION, score_features
from app.schemas import BatchScoreRequest, BatchScoreResponse, HealthResponse, ModelCardResponse, ScoreResponse

app = FastAPI(
    title="Hospital Readmission FHIR ML API",
    version="0.1.0",
    description="Synthetic FHIR-style readmission risk scoring demo. Not for clinical use.",
)

BASE_DIR = Path(__file__).resolve().parents[1]


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", model_version=MODEL_VERSION, data_notice=DATA_NOTICE)


@app.get("/model/card", response_model=ModelCardResponse)
def model_card() -> ModelCardResponse:
    return ModelCardResponse(
        model_version=MODEL_VERSION,
        intended_use="Synthetic portfolio demo of a readmission-risk API architecture.",
        limitations=[
            "Not trained on real patient data.",
            "Not clinically validated.",
            "Not intended for diagnosis, treatment, or live clinical decision support.",
            "Uses deterministic transparent coefficients for easy local validation.",
        ],
        feature_groups=[
            "demographics",
            "utilization",
            "comorbidities",
            "medication complexity",
            "labs and observations",
            "discharge context",
        ],
        data_notice=DATA_NOTICE,
    )


@app.get("/schema/example")
def schema_example() -> dict[str, Any]:
    return _load_example("synthetic_fhir_bundle_medium_risk.json")


@app.post("/score/fhir-bundle", response_model=ScoreResponse)
def score_fhir_bundle(payload: dict[str, Any]) -> ScoreResponse:
    bundle = _coerce_bundle(payload)
    return _score(bundle)


@app.post("/score/batch", response_model=BatchScoreResponse)
def score_batch(payload: BatchScoreRequest) -> BatchScoreResponse:
    return BatchScoreResponse(
        model_version=MODEL_VERSION,
        results=[_score(bundle) for bundle in payload.bundles],
    )


def _score(bundle: dict[str, Any]) -> ScoreResponse:
    features = build_features(bundle)
    probability, band = score_features(features)
    return ScoreResponse(
        patient_id=patient_id(bundle),
        model_version=MODEL_VERSION,
        readmission_risk_probability=probability,
        risk_band=band,  # type: ignore[arg-type]
        top_features=top_features(features, limit=5),
        data_notice=DATA_NOTICE,
    )


def _coerce_bundle(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("resourceType") == "Bundle":
        return payload
    bundle = payload.get("bundle")
    if isinstance(bundle, dict) and bundle.get("resourceType") == "Bundle":
        return bundle
    raise HTTPException(status_code=422, detail="Request body must be a FHIR-style Bundle or {bundle: Bundle}.")


def _load_example(filename: str) -> dict[str, Any]:
    path = BASE_DIR / "data" / filename
    return json.loads(path.read_text(encoding="utf-8"))

