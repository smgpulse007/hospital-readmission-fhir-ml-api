"""Exercise the actual ASGI routes with bundled synthetic data, in-process."""
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


ROOT = Path(__file__).resolve().parents[1]


def main():
    print("Synthetic FHIR API walkthrough (in-process TestClient)")
    print("Fixed demo weights; not a trained or clinically validated model.\n")
    with TestClient(app) as client:
        response = client.get("/health")
        response.raise_for_status()
        print(f"GET /health -> {response.status_code} {response.json()['status']}\n")
        for label in ("low", "medium", "high"):
            fixture = ROOT / "data" / f"synthetic_fhir_bundle_{label}_risk.json"
            bundle = json.loads(fixture.read_text(encoding="utf-8"))
            response = client.post("/score/fhir-bundle", json=bundle)
            response.raise_for_status()
            payload = response.json()
            print(f"POST /score/fhir-bundle -> {response.status_code} | {label} fixture")
            print(f"  {payload['patient_id']}: demo score {payload['readmission_risk_probability']:.4f}, band {payload['risk_band']}")
            first = payload["top_features"][0]
            print(f"  Top contribution: {first['feature']} = {first['value']} ({first['direction']})\n")
        invalid = client.post("/score/fhir-bundle", json={"resourceType": "Patient"})
        if invalid.status_code != 422:
            raise RuntimeError(f"Expected malformed bundle rejection, got {invalid.status_code}")
        print(f"Malformed bundle -> {invalid.status_code} (expected rejection)")
    print("No network server, patient record, or external API is used in this walkthrough.")


if __name__ == "__main__":
    main()
