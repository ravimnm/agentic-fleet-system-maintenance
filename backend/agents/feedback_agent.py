from datetime import datetime
from typing import Dict, Any

from database.mongo_client import MongoConnection


class FeedbackAgent:
    def __init__(self, db: MongoConnection) -> None:
        self.db = db

    def handle(self, context: Dict[str, Any], prediction: Dict[str, Any], risk: Dict[str, Any]) -> Dict[str, Any]:
        telemetry = context["telemetry"]
        doc = {
            "vehicleId": telemetry.get("vehicleId"),
            "timestamp": telemetry.get("timestamp", datetime.utcnow().isoformat()),
            "source": "FeedbackAgent",
            "status": "awaiting_feedback",
            "notes": f"Prediction {prediction.get('predicted_event')} with risk {risk.get('risk_score', 0):.2f}",
        }
        self.db.insert("feedback", doc)
        self.db.insert(
            "agent_actions",
            {
                "vehicleId": doc["vehicleId"],
                "timestamp": doc["timestamp"],
                "source": "FeedbackAgent",
                "action": "Requested driver/technician feedback",
                "reason": doc["notes"],
            },
        )
        return doc

