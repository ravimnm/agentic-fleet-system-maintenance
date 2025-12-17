from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from agents.master_agent import MasterAgent
from database.mongo_client import MongoConnection
from dependencies import get_db, get_master_agent, get_current_user
from utils.time_utils import ensure_timestamp

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("")
async def predict(
    payload: Dict[str, Any],
    master_agent: MasterAgent = Depends(get_master_agent),
    current_user: dict = Depends(get_current_user),
):
    if "vehicleId" not in payload:
        raise HTTPException(status_code=400, detail="vehicleId is required")
    # RBAC: users may only request predictions for their assigned vehicle
    if current_user.get("role") == "user":
        if current_user.get("vehicleId") is None or int(payload.get("vehicleId")) != int(current_user.get("vehicleId")):
            raise HTTPException(status_code=403, detail="Forbidden: cannot request predictions for this vehicle")
    payload["timestamp"] = ensure_timestamp(payload.get("timestamp"))
    return master_agent.process_telemetry(payload)


@router.get("/{vehicleId}")
async def latest_prediction(vehicleId: str, db: MongoConnection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # RBAC: users only allowed their vehicle
    if current_user.get("role") == "user":
        if current_user.get("vehicleId") is None or int(vehicleId) != int(current_user.get("vehicleId")):
            raise HTTPException(status_code=403, detail="Forbidden: access to this vehicle is denied")

    # try numeric vehicle id for consistency
    try:
        vid_query = int(vehicleId)
    except Exception:
        vid_query = vehicleId

    doc = db.find_one("predictions", {"vehicleId": vid_query}, sort=[("timestamp", -1)])
    if not doc:
        raise HTTPException(status_code=404, detail="No prediction found")

    doc["_id"] = str(doc["_id"])
    return doc

