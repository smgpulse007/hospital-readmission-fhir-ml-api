from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def bundle_entries(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [entry.get("resource", {}) for entry in bundle.get("entry", []) if entry.get("resource")]


def resources_by_type(bundle: dict[str, Any], resource_type: str) -> list[dict[str, Any]]:
    return [resource for resource in bundle_entries(bundle) if resource.get("resourceType") == resource_type]


def first_resource(bundle: dict[str, Any], resource_type: str) -> dict[str, Any] | None:
    resources = resources_by_type(bundle, resource_type)
    return resources[0] if resources else None


def patient_id(bundle: dict[str, Any]) -> str:
    patient = first_resource(bundle, "Patient") or {}
    return str(patient.get("id") or "synthetic-patient-unknown")


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            return None


def age_in_years(patient: dict[str, Any], as_of_year: int = 2026) -> int:
    birth_date = str(patient.get("birthDate") or "")
    if not birth_date:
        return 0
    try:
        return max(0, as_of_year - int(birth_date[:4]))
    except ValueError:
        return 0


def code_text(resource: dict[str, Any]) -> str:
    parts: list[str] = []
    code = resource.get("code") or {}
    if isinstance(code, dict):
        if code.get("text"):
            parts.append(str(code["text"]))
        for coding in code.get("coding", []) or []:
            parts.extend(str(coding.get(key, "")) for key in ("code", "display") if coding.get(key))
    return " ".join(parts).lower()


def observation_value(resource: dict[str, Any]) -> float | None:
    value = resource.get("valueQuantity", {}).get("value")
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

