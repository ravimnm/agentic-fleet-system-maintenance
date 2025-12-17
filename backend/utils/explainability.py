from typing import Dict, List


def explain(features: Dict[str, float], weights: Dict[str, float]) -> List[Dict[str, float]]:
    """
    Returns top 3 contributing features with impact score.
    The impact is a simple absolute product of feature value and supplied weight.
    """
    impacts = []
    for name, value in features.items():
        weight = weights.get(name, 1.0)
        try:
            impact = abs(float(value) * float(weight))
        except (TypeError, ValueError):
            continue
        impacts.append({"feature": name, "impact": round(impact, 4)})

    impacts.sort(key=lambda x: x["impact"], reverse=True)
    return impacts[:3]

