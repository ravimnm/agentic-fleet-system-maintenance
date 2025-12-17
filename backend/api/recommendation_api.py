from fastapi import APIRouter, Depends

from database.mongo_client import MongoConnection
from dependencies import get_db

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{vehicleId}")
async def recommendations(vehicleId: str, db: MongoConnection = Depends(get_db)):
    cursor = (
        db.get_collection("maintenance_recommendations")
        .find({"vehicleId": vehicleId})
        .sort("timestamp", -1)
        .limit(50)
    )
    docs = list(cursor)
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs

