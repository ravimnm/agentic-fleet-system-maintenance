from fastapi import APIRouter, Depends

from database.mongo_client import MongoConnection
from dependencies import get_db

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
async def list_alerts(db: MongoConnection = Depends(get_db)):
    cursor = (
        db.get_collection("alerts")
        .find()
        .sort("timestamp", -1)
        .limit(100)
    )
    docs = list(cursor)
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs

