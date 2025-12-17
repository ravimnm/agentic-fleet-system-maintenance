from datetime import datetime
from typing import Dict, Any, List

from database.mongo_client import MongoConnection


class RuleAgent:
    def __init__(self, db: MongoConnection) -> None:
        self.db = db

    def handle(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        telemetry = context["telemetry"]
        alerts: List[Dict[str, Any]] = []
        timestamp = telemetry.get("timestamp", datetime.utcnow().isoformat())

        # tolerate multiple possible telemetry field names from CSVs / ingests
        vibration = telemetry.get("vibration")
        if vibration is None:
            vibration = telemetry.get("total_acceleration") or telemetry.get("totalAcceleration") or 0

        hard_brake_event = telemetry.get("hard_brake_event", telemetry.get("hardBrakeEvent", False))
        # coerce string booleans
        if isinstance(hard_brake_event, str):
            hard_brake_event = hard_brake_event.lower() == "true"

        speed = telemetry.get("speed") or telemetry.get("gps_speed") or telemetry.get("gpsSpeed") or 0
        angular_acc = telemetry.get("angular_acceleration") or telemetry.get("angularAcceleration") or 0

        if vibration > 0.8 and bool(hard_brake_event):
            alerts.append(
                {
                    "vehicleId": telemetry.get("vehicleId"),
                    "timestamp": timestamp,
                    "severity": "high",
                    "rule": "vibration_brake_combo",
                    "details": "High vibration with hard brake event",
                }
            )

        if speed > 100 and angular_acc > telemetry.get("angular_threshold", 0.5):
            alerts.append(
                {
                    "vehicleId": telemetry.get("vehicleId"),
                    "timestamp": timestamp,
                    "severity": "medium",
                    "rule": "speed_angular_combo",
                    "details": "High speed with elevated angular acceleration",
                }
            )

        for alert in alerts:
            self.db.insert("alerts", alert)

        return alerts

