from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from database.mongo_client import MongoConnection
from dependencies import get_db
from utils.time_utils import ensure_timestamp

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.post("")
async def create_vehicle(
    payload: Dict[str, Any],
    db: MongoConnection = Depends(get_db)
):
    if "vehicleId" not in payload:
        raise HTTPException(status_code=400, detail="vehicleId is required")

    payload["timestamp"] = ensure_timestamp(payload.get("timestamp"))
    payload["source"] = "vehicle_api"

    db.insert("vehicles", payload)
    return {"status": "vehicle created"}

@router.get("")
async def list_vehicles(db: MongoConnection = Depends(get_db)):
    return db.find("vehicles")

@router.get("/{vehicleId}")
async def get_vehicle(
    vehicleId: str,
    db: MongoConnection = Depends(get_db)
):
    doc = db.find_one("vehicles", {"vehicleId": vehicleId})
    if not doc:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return doc

@router.put("/{vehicleId}")
async def update_vehicle(
    vehicleId: str,
    updates: Dict[str, Any],
    db: MongoConnection = Depends(get_db)
):
    updated = db.update_one(
        "vehicles",
        {"vehicleId": vehicleId},
        {"$set": updates}
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"status": "vehicle updated"}

@router.delete("/{vehicleId}")
async def delete_vehicle(
    vehicleId: str,
    db: MongoConnection = Depends(get_db)
):
    deleted = db.delete_one("vehicles", {"vehicleId": vehicleId})
    if not deleted:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"status": "vehicle deleted"}
