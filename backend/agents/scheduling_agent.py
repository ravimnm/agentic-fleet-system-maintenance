from datetime import datetime, timedelta
from typing import Dict, Any

from database.mongo_client import MongoConnection


class SchedulingAgent:
    def __init__(self, db: MongoConnection) -> None:
        self.db = db

    def handle(
        self, context: Dict[str, Any], prediction: Dict[str, Any], risk: Dict[str, Any]
    ) -> Dict[str, Any]:
        telemetry = context["telemetry"]
        risk_score = risk.get("risk_score", 0.0)
        if risk_score >= 0.7:
            schedule_date = datetime.utcnow() + timedelta(days=1)
            priority = "urgent"
        elif risk_score >= 0.4:
            schedule_date = datetime.utcnow() + timedelta(days=7)
            priority = "standard"
        else:
            schedule_date = datetime.utcnow() + timedelta(days=30)
            priority = "low"

        doc = {
            "vehicleId": telemetry.get("vehicleId"),
            "timestamp": telemetry.get("timestamp", datetime.utcnow().isoformat()),
            "source": "SchedulingAgent",
            "scheduled_date": schedule_date.isoformat(),
            "priority": priority,
        }
        self.db.insert("maintenance_events", doc)
        self.db.insert(
            "agent_actions",
            {
                "vehicleId": doc["vehicleId"],
                "timestamp": doc["timestamp"],
                "source": "SchedulingAgent",
                "action": f"Maintenance scheduled ({priority})",
                "reason": f"Risk score {risk_score:.2f}",
            },
        )
        return doc

