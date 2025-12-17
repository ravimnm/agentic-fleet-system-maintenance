"""
Sync collections with telemetry data.
- Upsert entries into `vehicles` for any `vehicleId` present in `telemetry`.
- Add an initial `agent_timeline` entry for newly created vehicles.
Run from repository root:
  python backend/scripts/sync_collections.py
"""
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.mongo_client import MongoConnection


def main():
    db = MongoConnection()
    telemetry_col = db.get_collection("telemetry")
    vehicles_col = db.get_collection("vehicles")
    timeline_col = db.get_collection("agent_timeline")

    telemetry_ids = telemetry_col.distinct("vehicleId")
    telemetry_ids = sorted(set(telemetry_ids))

    created = 0
    updated = 0

    for vid in telemetry_ids:
        if vid is None:
            continue
        existing = vehicles_col.find_one({"vehicleId": vid})
        if existing:
            updated += 1
            continue
        doc = {
            "vehicleId": int(vid),
            "registeredAt": datetime.utcnow().isoformat(),
            "source": "telemetry_sync",
        }
        vehicles_col.insert_one(doc)
        created += 1

        # Add a short timeline entry for visibility
        timeline_col.insert_one(
            {
                "vehicleId": int(vid),
                "timestamp": doc["registeredAt"],
                "source": "sync_script",
                "event": "Vehicle registered from telemetry sync",
            }
        )

    print(f"Vehicles upserted: {created} (existing: {updated})")


if __name__ == '__main__':
    main()
