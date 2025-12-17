from fastapi import APIRouter, Depends, HTTPException
from database.mongo_client import MongoConnection
from dependencies import get_db, get_current_user

router = APIRouter(prefix="/fleet", tags=["fleet"])


@router.get("/overview")
async def overview(db: MongoConnection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: admin access required")
    # Count vehicles from telemetry distinct IDs to reflect ingested data
    try:
        telemetry_ids = db.get_collection("telemetry").distinct("vehicleId")
        vehicles = len(set(telemetry_ids))
    except Exception:
        # fallback to vehicles collection count
        vehicles = db.get_collection("vehicles").estimated_document_count()
    risk_cursor = db.get_collection("risk_logs").find().limit(200)
    risks = list(risk_cursor)
    high_risk = sum(1 for r in risks if r.get("category") == "high")
    avg_prob = 0.0
    preds = list(db.get_collection("predictions").find().limit(200))
    if preds:
        avg_prob = sum(p.get("probability", 0) for p in preds) / len(preds)
    return {
        "totalVehicles": vehicles,
        "highRisk": high_risk,
        "avgFailureProbability": round(avg_prob, 3),
    }


@router.get("/top-risk")
async def top_risk(db: MongoConnection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: admin access required")
    cursor = (
        db.get_collection("risk_logs")
        .find()
        .sort("risk_score", -1)
        .limit(10)
    )
    docs = list(cursor)
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs


@router.get("/agent-actions")
async def agent_actions(db: MongoConnection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden: admin access required")
    cursor = (
        db.get_collection("agent_actions")
        .find()
        .sort("timestamp", -1)
        .limit(50)
    )
    docs = list(cursor)
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs

