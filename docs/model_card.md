# Model Card

## Model

- Name: `readmission-risk-demo-v0.1.0`
- Family: deterministic XGBoost-style / gradient-boosted demo scorer
- Intended use: portfolio demonstration of a readmission-risk API architecture

## Data

All examples are synthetic FHIR-style bundles created for this repository. No PHI, PII, employer data, claims data, EHR exports, or proprietary workflows are included.

## Inputs

The scorer consumes engineered features derived from synthetic Patient, Encounter, Condition, MedicationRequest, Observation, and Procedure resources.

## Outputs

The service returns a probability-like risk score, a low/medium/high band, and the strongest feature contributions.

## Limitations

- Not trained on real patient data.
- Not clinically validated.
- Not appropriate for diagnosis, treatment, benefit decisions, or live clinical decision support.
- Coefficients are transparent demo weights, not measured production outcomes.

