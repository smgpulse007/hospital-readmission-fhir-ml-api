# Synthetic API recording

The GIF renders actual output from `python scripts/demo_api.py` and
`python -m pytest -q`. The walkthrough sends requests to the real FastAPI app
through its in-process TestClient, using only the three bundled synthetic FHIR
fixtures. It checks health, prints each response's score and top contribution,
and verifies that a malformed bundle returns 422. It does not connect to a live
hospital, launch a network server, or call an external API.

The response field retains the existing name `readmission_risk_probability`, but
its value is a sigmoid of hand-set weights, not a calibrated clinical probability.
The fixture labels and displayed scores are demonstrations, not validation data.

Install the documented development dependencies plus Pillow, then run
`python scripts/record_demo.py` to rebuild the animation. Full captured output
and source hashes are in `demo-recording.json`. Playback pauses are adjusted for
reading, not a latency benchmark. A TestClient dependency deprecation warning is
retained in the recording; it does not invalidate the passing checks. Local
absolute repository paths are replaced with `<repository>` before sharing; API
responses and test results are unchanged.
