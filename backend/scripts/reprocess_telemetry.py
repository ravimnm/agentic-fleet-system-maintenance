"""
Reprocess telemetry documents through MasterAgent to generate alerts and timeline entries.
Run from repository root with the backend environment vars set (MONGODB_URI, MONGODB_DB).
"""
import os
import sys

# Ensure backend package root is on sys.path so imports resolve when run from repo root
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.mongo_client import MongoConnection
from agents.rule_agent import RuleAgent


def main(limit=1000):
    db: MongoConnection = None
    try:
        from dependencies import get_db

        db = get_db()
    except Exception:
        # fallback: create a new connection
        from database.mongo_client import MongoConnection as MC

        db = MC()

    rule_agent = RuleAgent(db)

    cursor = db.get_collection("telemetry").find({}, sort=[("timestamp", -1)])
    count = 0
    for doc in cursor:
        try:
            alerts = rule_agent.handle({"telemetry": doc})
            if alerts:
                count += len(alerts)
        except Exception as e:
            print("Error processing doc", doc.get("_id"), e)
        if count >= limit:
            break

    print(f"Inserted {count} alerts from telemetry reprocessing")


if __name__ == '__main__':
    main()
