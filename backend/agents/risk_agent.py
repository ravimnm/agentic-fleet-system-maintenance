from datetime import datetime
from typing import Dict, Any

from database.mongo_client import MongoConnection


class RiskAgent:
    def __init__(self, db: MongoConnection) -> None:
        self.db = db

    def handle(
        self,
        context: Dict[str, Any],
        prediction: Dict[str, Any],
        diagnostics: Dict[str, Any],
    ) -> Dict[str, Any]:
        telemetry = context["telemetry"]
        base_prob = prediction.get("probability", 0.0)
        risk_score = min(1.0, base_prob + 0.1 * len(diagnostics.get("issues", [])))
        category = "high" if risk_score >= 0.7 else "medium" if risk_score >= 0.4 else "low"

        doc = {
            "vehicleId": telemetry.get("vehicleId"),
            "timestamp": telemetry.get("timestamp", datetime.utcnow().isoformat()),
            "source": "RiskAgent",
            "risk_score": risk_score,
            "category": category,
        }
        self.db.insert("risk_logs", doc)
        self.db.insert(
            "agent_actions",
            {
                "vehicleId": doc["vehicleId"],
                "timestamp": doc["timestamp"],
                "source": "RiskAgent",
                "action": f"Risk classified as {category}",
                "reason": f"Probability {base_prob:.2f}, issues {len(diagnostics.get('issues', []))}",
            },
        )
        return doc

