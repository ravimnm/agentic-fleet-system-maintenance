from datetime import datetime
from typing import Dict, Any

from database.mongo_client import MongoConnection


class DiagnosticsAgent:
    def __init__(self, db: MongoConnection) -> None:
        self.db = db

    def handle(self, context: Dict[str, Any], prediction: Dict[str, Any]) -> Dict[str, Any]:
        telemetry = context["telemetry"]
        issues = []
        reason = []

        # Simple rules for demo diagnostics
        if telemetry.get("rpm", 0) > 4000:
            issues.append("High RPM")
            reason.append("rpm > 4000")
        if telemetry.get("braking", 0) > 0.8:
            issues.append("Aggressive braking")
            reason.append("braking > 0.8")
        if telemetry.get("vibration", 0) > 0.7:
            issues.append("High vibration")
            reason.append("vibration > 0.7")

        doc = {
            "vehicleId": telemetry.get("vehicleId"),
            "timestamp": telemetry.get("timestamp", datetime.utcnow().isoformat()),
            "source": "DiagnosticsAgent",
            "issues": issues,
            "summary": "; ".join(reason) if reason else "No critical issues detected",
        }
        self.db.insert(
            "agent_actions",
            {
                "vehicleId": doc["vehicleId"],
                "timestamp": doc["timestamp"],
                "source": "DiagnosticsAgent",
                "action": "Diagnostics assessment",
                "reason": doc["summary"],
            },
        )
        return doc

