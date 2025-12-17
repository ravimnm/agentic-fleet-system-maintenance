from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException

from database.mongo_client import MongoConnection
from dependencies import get_db
from utils.time_utils import ensure_timestamp

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("")
async def submit_feedback(payload: Dict[str, Any], db: MongoConnection = Depends(get_db)):
    if "vehicleId" not in payload:
        raise HTTPException(status_code=400, detail="vehicleId is required")
    doc = {
        **payload,
        "timestamp": ensure_timestamp(payload.get("timestamp")),
        "source": payload.get("source", "user_feedback"),
    }
    db.insert("feedback", doc)
    return {"status": "ok"}

