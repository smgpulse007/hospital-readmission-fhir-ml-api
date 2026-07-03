# Architecture

This repository is a synthetic-data reference implementation for the public engineering shape of a readmission-risk service.

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI
    participant Parser as FHIR Parser
    participant Features as Feature Builder
    participant Model as Demo Scorer
    participant Explainer as Explainability

    Client->>API: POST /score/fhir-bundle
    API->>Parser: Validate Bundle shape
    Parser->>Features: Patient, Encounter, Condition, MedicationRequest, Observation, Procedure
    Features->>Model: Numeric feature vector
    Model->>Explainer: Probability and feature contributions
    Explainer-->>Client: Typed risk response
```

## Boundary

The service demonstrates API design, data contracts, feature extraction, explainability, and containerization. It does not demonstrate clinical validation, real-world model governance, EHR integration, or payer/provider production controls.

