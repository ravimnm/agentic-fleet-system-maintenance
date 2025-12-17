from datetime import datetime
from typing import Dict, Any

from database.mongo_client import MongoConnection


def log_timeline_entry(
    db: MongoConnection,
    vehicle_id: str,
    agent: str,
    decision: str,
    timestamp: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> None:
    """
    Persist a chronological agent decision entry for auditability.
    """
    entry = {
        "vehicleId": vehicle_id,
        "agent": agent,
        "decision": decision,
        "timestamp": timestamp or datetime.utcnow().isoformat(),
    }
    if metadata:
        entry["metadata"] = metadata
    db.insert("agent_timeline", entry)

