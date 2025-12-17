from fastapi import APIRouter, Depends, HTTPException

from database.mongo_client import MongoConnection
from dependencies import get_db, get_current_user

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/{vehicleId}")
async def latest_risk(
    vehicleId: str, db: MongoConnection = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    # RBAC: user role limited to their vehicle
    if current_user.get("role") == "user":
        if current_user.get("vehicleId") is None or int(vehicleId) != int(current_user.get("vehicleId")):
            raise HTTPException(status_code=403, detail="Forbidden: access to this vehicle is denied")

    doc = db.find_one("risk_logs", {"vehicleId": int(vehicleId)}, sort=[("timestamp", -1)])
    if not doc:
        return {"status": "no_risk_data", "message": "Risk not generated yet"}

    # ensure JSON-safe ids
    doc["_id"] = str(doc["_id"])
    return doc

