from __future__ import annotations

import json
from pathlib import Path

from app.model import FEATURE_WEIGHTS, INTERCEPT, MODEL_VERSION


def main() -> None:
    output_path = Path("models/readmission-risk-demo-v0.1.0.json")
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "model_version": MODEL_VERSION,
                "model_family": "deterministic gradient-boosted-style demo scorer",
                "intercept": INTERCEPT,
                "feature_weights": FEATURE_WEIGHTS,
                "training_data": "synthetic generated rows only",
                "clinical_status": "not clinically validated",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(f"Wrote model metadata to {output_path}")


if __name__ == "__main__":
    main()

