from __future__ import annotations

from app.model import feature_contributions
from app.schemas import TopFeature


def top_features(features: dict[str, float], limit: int = 5) -> list[TopFeature]:
    contributions = feature_contributions(features)
    ordered = sorted(contributions.items(), key=lambda item: abs(item[1]), reverse=True)
    output: list[TopFeature] = []
    for feature, contribution in ordered[:limit]:
        if contribution > 0:
            direction = "increases_risk"
        elif contribution < 0:
            direction = "decreases_risk"
        else:
            direction = "neutral"
        value = features.get(feature, 0)
        output.append(TopFeature(feature=feature, value=_format_value(value), direction=direction))
    return output


def _format_value(value: float) -> float | int:
    return int(value) if float(value).is_integer() else round(value, 2)

