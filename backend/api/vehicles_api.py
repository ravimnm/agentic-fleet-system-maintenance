from fastapi import APIRouter, Depends

from database.mongo_client import MongoConnection
from dependencies import get_db

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/list")
async def list_vehicles(db: MongoConnection = Depends(get_db)):
    """Get list of all vehicle IDs in the system."""
    # Use collection.distinct to reliably list vehicle identifiers
    cursor = db.get_collection("telemetry").distinct("vehicleId")
    vehicle_ids = sorted(list(set(cursor)))
    return {"vehicles": vehicle_ids, "count": len(vehicle_ids)}
