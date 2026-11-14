from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.fhir_parser import (
    age_in_years,
    code_text,
    first_resource,
    observation_value,
    parse_datetime,
    resources_by_type,
)


COMORBIDITY_KEYWORDS = {
    "diabetes": "has_diabetes",
    "heart failure": "has_chf",
    "congestive": "has_chf",
    "copd": "has_copd",
    "chronic obstructive": "has_copd",
    "kidney": "has_ckd",
    "renal": "has_ckd",
}


def build_features(bundle: dict[str, Any], as_of: datetime | None = None) -> dict[str, float]:
    as_of = _as_utc(as_of or datetime(2026, 1, 1, tzinfo=timezone.utc))
    patient = first_resource(bundle, "Patient") or {}
    encounters = resources_by_type(bundle, "Encounter")
    conditions = resources_by_type(bundle, "Condition")
    medications = resources_by_type(bundle, "MedicationRequest")
    observations = resources_by_type(bundle, "Observation")
    procedures = resources_by_type(bundle, "Procedure")

    condition_texts = [code_text(condition) for condition in conditions]
    condition_blob = " ".join(condition_texts)

    features: dict[str, float] = {
        "age": float(age_in_years(patient, as_of.year)),
        "age_over_75": 0.0,
        "prior_admissions_180d": 0.0,
        "emergency_visits_180d": 0.0,
        "index_length_of_stay_days": 0.0,
        "comorbidity_count": float(len({text for text in condition_texts if text})),
        "medication_count": float(len(medications)),
        "abnormal_lab_count": 0.0,
        "procedure_count": float(len(procedures)),
        "discharge_disposition_home_health": 0.0,
        "discharge_disposition_snf": 0.0,
        "has_diabetes": 0.0,
        "has_chf": 0.0,
        "has_copd": 0.0,
        "has_ckd": 0.0,
        "creatinine_high": 0.0,
        "hemoglobin_low": 0.0,
    }

    features["age_over_75"] = 1.0 if features["age"] >= 75 else 0.0

    for keyword, feature_name in COMORBIDITY_KEYWORDS.items():
        if keyword in condition_blob:
            features[feature_name] = 1.0

    # Select one index encounter; historical and emergency stays must not
    # contribute its length of stay or discharge disposition.
    inpatient_encounters = []
    for encounter in encounters:
        start = parse_datetime((encounter.get("period") or {}).get("start"))
        if (
            _encounter_class(encounter) in {"inpatient", "imp"}
            and start is not None
            and _as_utc(start) <= as_of
        ):
            inpatient_encounters.append((_as_utc(start), encounter))
    index_encounter = max(inpatient_encounters, key=lambda item: item[0])[1] if inpatient_encounters else None

    for encounter in encounters:
        encounter_class = _encounter_class(encounter)
        start = parse_datetime((encounter.get("period") or {}).get("start"))
        is_index_admission = encounter is index_encounter
        if (
            encounter_class in {"inpatient", "imp"}
            and not is_index_admission
            and _within_days(start, as_of, 180)
        ):
            features["prior_admissions_180d"] += 1.0
        if encounter_class in {"emergency", "emer"} and _within_days(start, as_of, 180):
            features["emergency_visits_180d"] += 1.0
        if not is_index_admission:
            continue
        features["index_length_of_stay_days"] = _length_of_stay_days(encounter)
        disposition = str(
            ((encounter.get("hospitalization") or {}).get("dischargeDisposition") or {}).get("text", "")
        ).lower()
        if "home health" in disposition:
            features["discharge_disposition_home_health"] = 1.0
        if "skilled nursing" in disposition or "snf" in disposition:
            features["discharge_disposition_snf"] = 1.0

    for observation in observations:
        text = code_text(observation)
        value = observation_value(observation)
        if value is None:
            continue
        if "creatinine" in text and value >= 1.5:
            features["creatinine_high"] = 1.0
            features["abnormal_lab_count"] += 1.0
        if "hemoglobin" in text and value < 11.0:
            features["hemoglobin_low"] = 1.0
            features["abnormal_lab_count"] += 1.0
        if "sodium" in text and (value < 135 or value > 145):
            features["abnormal_lab_count"] += 1.0

    return features


def _encounter_class(encounter: dict[str, Any]) -> str:
    value = encounter.get("class")
    if isinstance(value, dict):
        return str(value.get("code") or value.get("display") or "").lower()
    return str(value or "").lower()


def _within_days(start: datetime | None, as_of: datetime, days: int) -> bool:
    if start is None:
        return False
    delta = _as_utc(as_of) - _as_utc(start)
    return 0 <= delta.days <= days


def _length_of_stay_days(encounter: dict[str, Any]) -> float:
    period = encounter.get("period") or {}
    start = parse_datetime(period.get("start"))
    end = parse_datetime(period.get("end"))
    if not start or not end:
        return 0.0
    return max(0.0, (_as_utc(end) - _as_utc(start)).total_seconds() / 86400)


def _as_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
