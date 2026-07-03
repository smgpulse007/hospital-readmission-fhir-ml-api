from __future__ import annotations

import json
from pathlib import Path

from app.features import build_features

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def load_bundle(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def test_high_risk_feature_extraction() -> None:
    features = build_features(load_bundle("synthetic_fhir_bundle_high_risk.json"))
    assert features["prior_admissions_180d"] == 3
    assert features["comorbidity_count"] == 6
    assert features["has_chf"] == 1
    assert features["has_ckd"] == 1
    assert features["abnormal_lab_count"] == 3
    assert features["discharge_disposition_home_health"] == 1


def test_low_risk_feature_extraction() -> None:
    features = build_features(load_bundle("synthetic_fhir_bundle_low_risk.json"))
    assert features["comorbidity_count"] == 1
    assert features["abnormal_lab_count"] == 0
    assert features["discharge_disposition_home_health"] == 0

