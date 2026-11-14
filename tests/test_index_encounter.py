from datetime import datetime, timezone

from app.features import build_features


def encounter(start, end, disposition="home", encounter_class="IMP"):
    return {
        "resourceType": "Encounter",
        "class": {"code": encounter_class},
        "period": {"start": start, "end": end},
        "hospitalization": {"dischargeDisposition": {"text": disposition}},
    }


def features_for(*encounters):
    return build_features({"entry": [{"resource": item} for item in encounters]})


def test_historical_long_stay_and_disposition_do_not_contaminate_index():
    old = encounter("2025-10-01", "2025-10-21", "skilled nursing facility")
    current = encounter("2025-12-20", "2025-12-22", "home health")
    for entries in ((old, current), (current, old)):
        features = features_for(*entries)
        assert features["prior_admissions_180d"] == 1
        assert features["index_length_of_stay_days"] == 2
        assert features["discharge_disposition_snf"] == 0
        assert features["discharge_disposition_home_health"] == 1


def test_emergency_encounter_cannot_supply_index_features_even_with_same_start():
    current = encounter("2025-12-20", "2025-12-22")
    emergency = encounter("2025-12-20", "2025-12-30", "SNF", "EMER")
    features = features_for(current, emergency)
    assert features["index_length_of_stay_days"] == 2
    assert features["discharge_disposition_snf"] == 0
    assert features["emergency_visits_180d"] == 1


def test_no_valid_inpatient_start_leaves_index_features_zero():
    features = features_for(
        encounter(None, "2025-12-22", "SNF"),
        encounter("invalid", "2025-12-22", "home health"),
        encounter("2025-12-20", "2025-12-30", "SNF", "EMER"),
    )
    assert features["index_length_of_stay_days"] == 0
    assert features["discharge_disposition_snf"] == 0
    assert features["discharge_disposition_home_health"] == 0


def test_future_inpatient_is_not_index_or_prior_admission():
    features = features_for(
        encounter("2025-12-20", "2025-12-22"),
        encounter("2026-01-02", "2026-01-20", "SNF"),
    )
    assert features["index_length_of_stay_days"] == 2
    assert features["prior_admissions_180d"] == 0
    assert features["discharge_disposition_snf"] == 0


def test_mixed_timestamp_formats_use_utc_and_honor_as_of():
    bundle = {"entry": [{"resource": item} for item in (
        encounter("2025-12-20", "2025-12-22T00:00:00Z"),
        encounter("2025-12-23T01:00:00+01:00", "2025-12-25", "home health"),
    )]}
    early = build_features(bundle, as_of=datetime(2025, 12, 22))
    later = build_features(bundle, as_of=datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert early["index_length_of_stay_days"] == 2
    assert early["discharge_disposition_home_health"] == 0
    assert later["index_length_of_stay_days"] == 2
    assert later["discharge_disposition_home_health"] == 1
    assert later["prior_admissions_180d"] == 1
