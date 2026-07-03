from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas import BatchScoreRequest, FhirBundleRequest


def test_bundle_request_accepts_fhir_bundle() -> None:
    request = FhirBundleRequest(bundle={"resourceType": "Bundle", "entry": []})
    assert request.bundle["resourceType"] == "Bundle"


def test_bundle_request_rejects_non_bundle() -> None:
    with pytest.raises(ValidationError):
        FhirBundleRequest(bundle={"resourceType": "Patient"})


def test_batch_request_requires_bundles() -> None:
    request = BatchScoreRequest(bundles=[{"resourceType": "Bundle", "entry": []}])
    assert len(request.bundles) == 1

