from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from math import radians, sin, cos, sqrt, atan2

from database.mongo_client import MongoConnection
from dependencies import get_db, get_current_user

router = APIRouter(prefix="/assistant", tags=["assistant"])


def haversine(lat1, lon1, lat2, lon2):
    # returns distance in kilometers
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


@router.post("/chat")
async def chat(payload: Dict[str, Any], db: MongoConnection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Simple rule-based assistant that answers from telemetry, risk, predictions, and recommendations.

    Payload: { vehicleId: int, question: str }
    """
    if "vehicleId" not in payload:
        raise HTTPException(status_code=400, detail="vehicleId is required")

    vehicleId = int(payload["vehicleId"])
    question = (payload.get("question") or "").lower()

    # RBAC: user role limited to their vehicle
    if current_user.get("role") == "user":
        if current_user.get("vehicleId") is None or int(vehicleId) != int(current_user.get("vehicleId")):
            raise HTTPException(status_code=403, detail="Forbidden: access to this vehicle is denied")

    # fetch context
    risk = db.find_one("risk_logs", {"vehicleId": vehicleId}, sort=[("timestamp", -1)])
    prediction = db.find_one("predictions", {"vehicleId": vehicleId}, sort=[("timestamp", -1)])
    recs_cursor = db.get_collection("maintenance_recommendations").find({"vehicleId": vehicleId}).sort("timestamp", -1).limit(5)
    recs = list(recs_cursor)

    # build answer heuristically
    parts = []
    if "risk" in question or "risky" in question or "why" in question:
        if risk:
            parts.append(f"Latest risk level: {risk.get('category')} (score {risk.get('risk_score')}).")
            if risk.get("reasons"):
                parts.append("Key reasons: " + ", ".join(risk.get("reasons")))
        else:
            parts.append("No recent risk assessment found for this vehicle.")

    if "fix" in question or "what should i" in question or "recommend" in question:
        if recs:
            top = recs[0]
            parts.append("Top recommendation: " + top.get("recommendation", "Check maintenance logs."))
        else:
            parts.append("No specific recommendations found; inspect high-risk components first.")

    if "safe" in question or "drive" in question:
        if risk and risk.get("category") == "high":
            parts.append("Warning: risk level is HIGH — not recommended to drive without inspection.")
        elif prediction and prediction.get("event") == "Breakdown":
            parts.append("Prediction indicates a breakdown may occur soon — exercise caution.")
        else:
            parts.append("No immediate safety concerns detected in recent data.")

    # fallback: summarize key facts
    if not parts:
        summary = []
        if risk:
            summary.append(f"risk={risk.get('category')}")
        if prediction:
            summary.append(f"prediction={prediction.get('event')} (p={prediction.get('probability')})")
        if recs:
            summary.append(f"recommendations={len(recs)} available")
        if summary:
            parts.append("Summary: " + "; ".join(summary))
        else:
            parts.append("I couldn't find relevant telemetry, risk, or prediction data for this vehicle.")

    answer = " ".join(parts)

    return {"answer": answer, "sources": {"risk": bool(risk), "prediction": bool(prediction), "recommendations": len(recs)}}


@router.get("/assistance/{vehicleId}")
async def assistance(vehicleId: str, db: MongoConnection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    vid = int(vehicleId)
    # RBAC: users only
    if current_user.get("role") == "user":
        if current_user.get("vehicleId") is None or int(vid) != int(current_user.get("vehicleId")):
            raise HTTPException(status_code=403, detail="Forbidden: access to this vehicle is denied")

    # last known location
    last_telemetry = db.find_one("telemetry", {"vehicleId": vid}, sort=[("timestamp", -1)])
    if not last_telemetry:
        raise HTTPException(status_code=404, detail="No telemetry location available for vehicle")

    lat = last_telemetry.get("lat") or last_telemetry.get("latitude")
    lng = last_telemetry.get("lng") or last_telemetry.get("longitude")
    if lat is None or lng is None:
        raise HTTPException(status_code=400, detail="Telemetry does not contain location coordinates")

    centers_cursor = db.get_collection("service_centers").find()
    centers = []
    for c in centers_cursor:
        c_lat = c.get("lat")
        c_lng = c.get("lng")
        if c_lat is None or c_lng is None:
            continue
        dist = haversine(float(lat), float(lng), float(c_lat), float(c_lng))
        centers.append({"center": c, "distance_km": dist})

    if not centers:
        raise HTTPException(status_code=404, detail="No service centers available")

    # sort and rank: open status, distance, rating
    open_centers = [c for c in centers if c["center"].get("open")]
    open_centers.sort(key=lambda x: (x["distance_km"], -float(x["center"].get("rating", 0))))

    centers.sort(key=lambda x: (x["distance_km"], -float(x["center"].get("rating", 0))))

    nearest_open = open_centers[0] if open_centers else None
    best_rated = sorted(centers, key=lambda x: (-float(x["center"].get("rating", 0)), x["distance_km"]))[0]

    def serial(cobj):
        c = cobj["center"].copy()
        c["_id"] = str(c["_id"]) if c.get("_id") is not None else None
        c["distance_km"] = round(cobj["distance_km"], 3)
        return c

    return {"nearest_open_center": serial(nearest_open) if nearest_open else None, "best_rated_center": serial(best_rated)}


@router.get("/assist/breakdown/{vehicleId}")
async def assist_breakdown(vehicleId: str, db: MongoConnection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Compatibility endpoint for frontend: returns { breakdown: bool, service_centers: [...] }"""
    vid = int(vehicleId)
    if current_user.get("role") == "user":
        if current_user.get("vehicleId") is None or int(vid) != int(current_user.get("vehicleId")):
            raise HTTPException(status_code=403, detail="Forbidden: access to this vehicle is denied")

    last_telemetry = db.find_one("telemetry", {"vehicleId": vid}, sort=[("timestamp", -1)])
    if not last_telemetry:
        return {"breakdown": False, "service_centers": []}

    lat = last_telemetry.get("lat") or last_telemetry.get("latitude")
    lng = last_telemetry.get("lng") or last_telemetry.get("longitude")
    if lat is None or lng is None:
        return {"breakdown": False, "service_centers": []}

    centers_cursor = db.get_collection("service_centers").find()
    centers = []
    for c in centers_cursor:
        c_lat = c.get("lat") or c.get("latitude")
        c_lng = c.get("lng") or c.get("longitude")
        if c_lat is None or c_lng is None:
            continue
        dist = haversine(float(lat), float(lng), float(c_lat), float(c_lng))
        centers.append({"center": c, "distance_km": dist})

    if not centers:
        return {"breakdown": False, "service_centers": []}

    centers.sort(key=lambda x: (x["distance_km"], -float(x["center"].get("rating", 0))))

    def serial_center(cobj):
        c = cobj["center"].copy()
        return {
            "_id": str(c.get("_id")) if c.get("_id") is not None else None,
            "name": c.get("name"),
            "address": c.get("address"),
            "distance_km": round(cobj["distance_km"], 3),
            "rating": c.get("rating"),
            "phone": c.get("phone"),
            "latitude": c.get("lat") or c.get("latitude"),
            "longitude": c.get("lng") or c.get("longitude"),
            "open": c.get("open", False),
        }

    service_centers = [serial_center(c) for c in centers]

    recent_pred = db.find_one("predictions", {"vehicleId": vid}, sort=[("timestamp", -1)])
    recent_risk = db.find_one("risk_logs", {"vehicleId": vid}, sort=[("timestamp", -1)])
    breakdown_flag = False
    if recent_pred and recent_pred.get("event") == "Breakdown":
        breakdown_flag = True
    if recent_risk and recent_risk.get("category") == "high":
        breakdown_flag = True

    return {"breakdown": breakdown_flag, "service_centers": service_centers}
