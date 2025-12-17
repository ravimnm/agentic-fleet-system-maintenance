from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from math import radians, sin, cos, sqrt, atan2

from database.mongo_client import MongoConnection
from dependencies import get_db, get_current_user

router = APIRouter(prefix="/bot", tags=["bot"])


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


@router.post("/chat")
async def chat(payload: Dict[str, Any], db: MongoConnection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Rule-based bot responding from local DB fields with enhanced responses.

    payload expected: { vehicleId: int, message: str }
    """
    if "vehicleId" not in payload:
        raise HTTPException(status_code=400, detail="vehicleId is required")

    vid = int(payload["vehicleId"])
    message = (payload.get("message") or "").lower()

    # RBAC
    if current_user.get("role") == "user":
        if current_user.get("vehicleId") is None or int(vid) != int(current_user.get("vehicleId")):
            raise HTTPException(status_code=403, detail="Forbidden: access to this vehicle is denied")

    # fetch contextual data
    risk = db.find_one("risk_logs", {"vehicleId": vid}, sort=[("timestamp", -1)])
    prediction = db.find_one("predictions", {"vehicleId": vid}, sort=[("timestamp", -1)])
    telemetry = db.find_one("telemetry", {"vehicleId": vid}, sort=[("timestamp", -1)])
    recs = list(db.get_collection("maintenance_recommendations").find({"vehicleId": vid}).sort("timestamp", -1).limit(5))
    service_centers = list(db.get_collection("service_centers").find({"open_now": True}).limit(10))

    # Intent: Explain health status
    if any(k in message for k in ["explain", "health", "status"]):
        if risk or prediction or telemetry:
            resp = []
            if risk:
                resp.append(f"🔴 Risk Status: {risk.get('category').upper()} (score {risk.get('risk_score'):.2f})")
            if prediction:
                resp.append(f"⚠️ Prediction: {prediction.get('event') or prediction.get('predicted_event')} ({prediction.get('probability')*100:.1f}% probability)")
            if telemetry:
                resp.append(f"📍 Last Location: {telemetry.get('latitude', 'N/A')}, {telemetry.get('longitude', 'N/A')}")
            if risk and risk.get("reasons"):
                resp.append(f"📋 Reasons: {', '.join(risk.get('reasons', []))}")
            return {"answer": "\n".join(resp)}
        return {"answer": "No vehicle data available for analysis."}

    # Intent: Why is it risky
    if any(k in message for k in ["why", "risky", "reason"]):
        if risk and risk.get("reasons"):
            return {"answer": f"Your vehicle is {risk.get('category').upper()} risk due to:\n• " + "\n• ".join(risk.get("reasons")) + f"\n\nRisk Score: {risk.get('risk_score'):.2f}"}
        return {"answer": "No detailed risk analysis available. Please check with a technician."}

    # Intent: Recommendations
    if any(k in message for k in ["what should i do", "fix", "recommend", "maintenance"]):
        if recs:
            resp = ["Recommended Actions:\n"]
            for idx, rec in enumerate(recs[:3], 1):
                resp.append(f"{idx}. {rec.get('recommendation', rec.get('component', 'Vehicle inspection'))}")
            return {"answer": "\n".join(resp)}
        return {"answer": "No specific recommendations available. Consider scheduling a maintenance check."}

    # Intent: Latest prediction
    if any(k in message for k in ["prediction", "predict", "fail"]):
        if prediction:
            event = prediction.get('event') or prediction.get('predicted_event')
            prob = prediction.get('probability', 0)
            resp = f"🔮 Latest Prediction:\nEvent: {event}\nProbability: {prob*100:.1f}%\n"
            if prob > 0.7:
                resp += "⚠️ High probability - consider immediate maintenance"
            return {"answer": resp}
        return {"answer": "No prediction data available."}

    # Intent: Service centers
    if any(k in message for k in ["service", "center", "repair", "garage", "nearby"]):
        if service_centers:
            resp = ["Available Service Centers (Open Now):\n"]
            for idx, center in enumerate(service_centers[:3], 1):
                rating = center.get('rating', 'N/A')
                phone = center.get('phone', 'Contact for details')
                resp.append(f"{idx}. {center.get('name', 'Service Center')} ⭐ {rating}\n   📞 {phone}")
            resp.append("\n💡 For emergency assistance, ask 'nearest service center' for distance calculations")
            return {"answer": "\n".join(resp)}
        return {"answer": "No service centers available currently. Call roadside assistance for help."}

    # Intent: Telemetry details
    if any(k in message for k in ["telemetry", "sensor", "data", "temperature", "pressure", "rpm"]):
        if telemetry:
            resp = ["Current Vehicle Telemetry:\n"]
            for key in ["temperature", "pressure", "rpm", "fuel", "voltage", "lat", "lng"]:
                if key in telemetry:
                    resp.append(f"• {key.upper()}: {telemetry[key]}")
            return {"answer": "\n".join(resp)}
        return {"answer": "No telemetry data available."}

    # Intent: Breakdown assistance
    if any(k in message for k in ["breakdown", "emergency", "help", "accident", "assistance"]):
        risk_score = float(risk.get("risk_score", 0)) if risk else 0.0
        prob = float(prediction.get("probability", 0)) if prediction else 0.0
        if risk_score > 0.8 or prob > 0.85:
            resp = ["🚨 BREAKDOWN ASSISTANCE\n"]
            resp.append("Your vehicle requires immediate assistance.\n")
            if service_centers:
                closest = service_centers[0]
                resp.append(f"Nearest Service Center: {closest.get('name')}\n")
                resp.append(f"📞 {closest.get('phone', 'Contact for details')}\n")
                resp.append(f"📍 Address: {closest.get('address', 'Check GPS')}\n")
                resp.append(f"⭐ Rating: {closest.get('rating', 'N/A')}")
            return {"answer": "\n".join(resp)}
        return {"answer": "Your vehicle status is stable. No emergency assistance needed at this time."}

    # Fallback: Comprehensive summary
    summary = []
    summary.append("📊 Vehicle Summary:\n")
    if risk:
        summary.append(f"Risk Level: {risk.get('category').upper()} ({risk.get('risk_score'):.2f})")
    if prediction:
        summary.append(f"Predicted Issue: {prediction.get('event') or prediction.get('predicted_event')}")
    if recs:
        summary.append(f"Recommended Actions: {len(recs)} pending")
    if service_centers:
        summary.append(f"Open Service Centers: {len(service_centers)} available")
    
    if len(summary) > 1:
        return {"answer": "\n".join(summary)}

    return {"answer": "I couldn't find relevant data. Try asking:\n• Explain my health\n• Why is it risky\n• What should I do\n• Where are service centers\n• Show me telemetry"}


@router.get("/assist/breakdown/{vehicleId}")
async def breakdown_assist(vehicleId: str, db: MongoConnection = Depends(get_db), current_user: dict = Depends(get_current_user)):
    vid = int(vehicleId)

    # RBAC
    if current_user.get("role") == "user":
        if current_user.get("vehicleId") is None or int(vid) != int(current_user.get("vehicleId")):
            raise HTTPException(status_code=403, detail="Forbidden: access to this vehicle is denied")

    # get latest risk and prediction
    risk = db.find_one("risk_logs", {"vehicleId": vid}, sort=[("timestamp", -1)])
    prediction = db.find_one("predictions", {"vehicleId": vid}, sort=[("timestamp", -1)])

    risk_score = float(risk.get("risk_score", 0)) if risk else 0.0
    prob = float(prediction.get("probability", 0)) if prediction else 0.0

    # trigger condition
    if not (risk_score > 0.8 or prob > 0.85):
        return {"breakdown": False, "message": "No breakdown condition detected."}

    # last location
    telemetry = db.find_one("telemetry", {"vehicleId": vid}, sort=[("timestamp", -1)])
    if not telemetry:
        raise HTTPException(status_code=404, detail="No telemetry location available")

    lat = telemetry.get("lat") or telemetry.get("latitude")
    lng = telemetry.get("lng") or telemetry.get("longitude")
    if lat is None or lng is None:
        raise HTTPException(status_code=400, detail="Telemetry lacks coordinates")

    centers_cursor = db.get_collection("service_centers").find({"open_now": True})
    centers = []
    for c in centers_cursor:
        c_lat = c.get("latitude")
        c_lng = c.get("longitude")
        if c_lat is None or c_lng is None:
            continue
        dist = haversine(float(lat), float(lng), float(c_lat), float(c_lng))
        centers.append({"center": c, "distance_km": dist})

    if not centers:
        return {"breakdown": True, "service_centers": []}

    # Build serializable list with distance and rating, sort by rating desc then distance asc
    def serial(cobj):
        c = cobj["center"].copy()
        c["_id"] = str(c.get("_id")) if c.get("_id") is not None else None
        c["distance_km"] = round(cobj["distance_km"], 3)
        c["rating"] = float(c.get("rating", 0)) if c.get("rating") is not None else 0.0
        return c

    centers_serial = [serial(c) for c in centers]
    centers_serial.sort(key=lambda c: (-c.get("rating", 0), c.get("distance_km", 9999)))

    # keep backwards compatibility by exposing best_rated and nearest_open
    best_rated = centers_serial[0]
    centers_by_distance = sorted(centers_serial, key=lambda c: (c.get("distance_km", 9999), -c.get("rating", 0)))
    nearest_open = centers_by_distance[0]

    return {"breakdown": True, "service_centers": centers_serial, "best_rated": best_rated, "nearest_open": nearest_open}
