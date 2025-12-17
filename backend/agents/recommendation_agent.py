from datetime import datetime
from typing import Dict, Any, List

from database.mongo_client import MongoConnection


class RecommendationAgent:
    def __init__(self, db: MongoConnection) -> None:
        self.db = db

    def handle(self, context: Dict[str, Any], risk: Dict[str, Any], diagnostics: Dict[str, Any]) -> List[Dict[str, Any]]:
        telemetry = context["telemetry"]
        timestamp = telemetry.get("timestamp", datetime.utcnow().isoformat())
        recommendations: List[Dict[str, Any]] = []

        risk_score = risk.get("risk_score", 0.0)
        issues = diagnostics.get("issues", [])

        if risk_score >= 0.7 or "High vibration" in issues:
            recommendations.append(
                {
                    "vehicleId": telemetry.get("vehicleId"),
                    "component": "drivetrain",
                    "recommendation": "Inspect drivetrain vibration mounts within 24 hours",
                    "severity": "high",
                    "timestamp": timestamp,
                }
            )

        if telemetry.get("braking", 0) > 0.6:
            recommendations.append(
                {
                    "vehicleId": telemetry.get("vehicleId"),
                    "component": "brakes",
                    "recommendation": "Inspect brake pads within 48 hours",
                    "severity": "medium",
                    "timestamp": timestamp,
                }
            )

        if not recommendations:
            recommendations.append(
                {
                    "vehicleId": telemetry.get("vehicleId"),
                    "component": "general",
                    "recommendation": "No immediate maintenance required",
                    "severity": "low",
                    "timestamp": timestamp,
                }
            )

        for rec in recommendations:
            self.db.insert("maintenance_recommendations", rec)

        return recommendations

