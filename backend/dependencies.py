from functools import lru_cache
from database.mongo_client import MongoConnection
from agents.master_agent import MasterAgent
from fastapi import Depends, Header, HTTPException


async def get_current_user(x_user_id: str | None = Header(None), db: MongoConnection = Depends(lambda: get_db())):
    """Mocked current user dependency.

    - If `X-User-Id` header is provided, attempt to load from `users` collection.
    - If not found, derive a simple mock from the id (admin_/user_). Default to admin.
    """
    # Default to a safe admin if no header provided
    if not x_user_id:
        return {"userId": "admin_1", "role": "admin"}

    # try to find a persisted user
    user = None
    try:
        db_conn = get_db()
        user = db_conn.find_one("users", {"userId": x_user_id})
    except Exception:
        user = None

    if user:
        # normalize user document
        return {
            "userId": user.get("userId"),
            "role": user.get("role", "user"),
            "vehicleId": user.get("vehicleId"),
        }

    # fallback mocked user inference
    if x_user_id.startswith("admin"):
        return {"userId": x_user_id, "role": "admin"}

    # try to parse vehicleId from id like user_12
    parts = x_user_id.split("_")
    vehicle_id = None
    if len(parts) > 1 and parts[-1].isdigit():
        vehicle_id = int(parts[-1])

    return {"userId": x_user_id, "role": "user", "vehicleId": vehicle_id}


@lru_cache
def get_db() -> MongoConnection:
    return MongoConnection()


@lru_cache
def get_master_agent() -> MasterAgent:
    db = get_db()
    return MasterAgent(db)

