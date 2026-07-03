from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_bundle(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_score_high_risk_bundle() -> None:
    response = client.post(
        "/score/fhir-bundle",
        json=load_bundle("synthetic_fhir_bundle_high_risk.json"),
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["patient_id"] == "synthetic-patient-003"
    assert payload["risk_band"] == "high"
    assert payload["readmission_risk_probability"] >= 0.65
    assert payload["top_features"]


def test_batch_score() -> None:
    response = client.post(
        "/score/batch",
        json={
            "bundles": [
                load_bundle("synthetic_fhir_bundle_low_risk.json"),
                load_bundle("synthetic_fhir_bundle_medium_risk.json"),
            ]
        },
    )
    assert response.status_code == 200
    assert len(response.json()["results"]) == 2

