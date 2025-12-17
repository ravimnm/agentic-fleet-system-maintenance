from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
import pandas as pd

from database.mongo_client import MongoConnection
from agents.master_agent import MasterAgent
from dependencies import get_db, get_master_agent
from utils.time_utils import ensure_timestamp
from utils.csv_validator import validate_dataframe

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

@router.post("/ingest")
async def ingest_telemetry(
    payload: Dict[str, Any] | List[Dict[str, Any]] = Body(None),
    file: UploadFile | None = File(None),
    db: MongoConnection = Depends(get_db),
    master_agent: MasterAgent = Depends(get_master_agent),
):
    records: List[Dict[str, Any]] = []

    if file:
        df = pd.read_csv(file.file)
        # normalize possible CSV column `timeStamp` -> `timestamp`
        if "timeStamp" in df.columns:
            df = df.rename(columns={"timeStamp": "timestamp"})

        is_valid, error = validate_dataframe(df)
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid telemetry CSV format", "message": error},
            )
        records = df.to_dict(orient="records")

    elif payload:
        records = payload if isinstance(payload, list) else [payload]

    else:
        raise HTTPException(status_code=400, detail="No telemetry payload provided")

    inserted = 0
    responses = []

    for rec in records:
        if "vehicleId" not in rec:
            raise HTTPException(status_code=400, detail="vehicleId is required")

        # 🔥 FORCE schema consistency
        rec["vehicleId"] = int(rec["vehicleId"])

        # normalize timestamp field (accept timeStamp from legacy CSVs)
        if "timestamp" not in rec and "timeStamp" in rec:
            rec["timestamp"] = rec.pop("timeStamp")
        if "timestamp" not in rec:
            raise HTTPException(status_code=400, detail="timestamp is required")

        rec["source"] = rec.get("source", "ingest_api")

        db.insert("telemetry", rec)
        inserted += 1

        responses.append(master_agent.process_telemetry(rec))

    return {"inserted": inserted, "results": responses}
from bson import ObjectId
from dependencies import get_current_user


@router.get("/latest/{vehicleId}")
async def latest_vehicle(
    vehicleId: str,
    db: MongoConnection = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Role-based access control: users may only access their own vehicle
    if current_user.get("role") == "user":
        if current_user.get("vehicleId") is None or int(vehicleId) != int(current_user.get("vehicleId")):
            raise HTTPException(status_code=403, detail="Forbidden: access to this vehicle is denied")
    doc = db.find_one(
        "telemetry",
        {"vehicleId": int(vehicleId)},
        sort=[("timestamp", -1)]
    )

    if not doc:
        raise HTTPException(status_code=404, detail="No telemetry found")

    # 🔥 FIX: make Mongo JSON-safe
    doc["_id"] = str(doc["_id"])

    return doc
