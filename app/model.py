from __future__ import annotations

import math

MODEL_VERSION = "readmission-risk-demo-v0.1.0"
DATA_NOTICE = "Synthetic portfolio demo only. No PHI/PII. Not for clinical use."

INTERCEPT = -3.1

FEATURE_WEIGHTS: dict[str, float] = {
    "age": 0.008,
    "age_over_75": 0.25,
    "prior_admissions_180d": 0.55,
    "emergency_visits_180d": 0.25,
    "index_length_of_stay_days": 0.06,
    "comorbidity_count": 0.18,
    "medication_count": 0.04,
    "abnormal_lab_count": 0.20,
    "procedure_count": 0.02,
    "discharge_disposition_home_health": 0.35,
    "discharge_disposition_snf": 0.40,
    "has_diabetes": 0.16,
    "has_chf": 0.25,
    "has_copd": 0.18,
    "has_ckd": 0.22,
    "creatinine_high": 0.18,
    "hemoglobin_low": 0.15,
}


def score_features(features: dict[str, float]) -> tuple[float, str]:
    logit = INTERCEPT + sum(FEATURE_WEIGHTS.get(name, 0.0) * value for name, value in features.items())
    probability = 1 / (1 + math.exp(-logit))
    return round(probability, 2), risk_band(probability)


def risk_band(probability: float) -> str:
    if probability >= 0.65:
        return "high"
    if probability >= 0.35:
        return "medium"
    return "low"


def feature_contributions(features: dict[str, float]) -> dict[str, float]:
    return {name: FEATURE_WEIGHTS.get(name, 0.0) * value for name, value in features.items()}
