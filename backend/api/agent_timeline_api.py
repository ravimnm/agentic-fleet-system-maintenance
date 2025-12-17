from fastapi import APIRouter, Depends

from database.mongo_client import MongoConnection
from dependencies import get_db

router = APIRouter(prefix="/agent-timeline", tags=["agent-timeline"])


@router.get("/{vehicleId}")
async def timeline(vehicleId: str, db: MongoConnection = Depends(get_db)):
    # Convert vehicleId to int if possible
    try:
        vid_int = int(vehicleId)
    except ValueError:
        vid_int = None
    
    # Query for both integer and string vehicleId formats
    or_clauses = []
    if vid_int is not None:
        or_clauses.append({"vehicleId": vid_int})
    or_clauses.append({"vehicleId": vehicleId})
    
    query = {"$or": or_clauses}
    
    cursor = (
        db.get_collection("agent_actions")
        .find(query)
        .sort("timestamp", -1)
        .limit(100)
    )
    docs = list(cursor)
    result = []
    for doc in docs:
        result.append({
            "timestamp": doc.get("timestamp"),
            "agent": doc.get("agent", "System"),
            "decision": doc.get("decision") or doc.get("action", "No details"),
        })
    return result

