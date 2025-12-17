from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from dependencies import get_db
from dependencies import get_current_user
from api import (
    telemetry_api,
    prediction_api,
    risk_api,
    fleet_api,
    feedback_api,
    alerts_api,
    agent_timeline_api,
    recommendation_api,
    vehicles_api,
    # assistant API
    assistant_api,
)
from routes import bot as bot_router

# --------------------------------------------------
# APP INITIALIZATION
# --------------------------------------------------

app = FastAPI(
    title="Agentic Fleet Predictive Maintenance & Risk Intelligence",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# STARTUP BOOTSTRAP
# --------------------------------------------------

@app.on_event("startup")
def bootstrap_data():
    """
    Bootstrap telemetry & vehicle data from CSV if telemetry is empty.
    This enables instant demo usage without manual DB setup.
    """

    try:
        db = get_db()
    except Exception as e:
        # DB not available → API still starts
        print("⚠️  Startup warning: database unavailable →", e)
        return

    try:
        telemetry_count = db.get_collection("telemetry").estimated_document_count()
        if telemetry_count > 0:
            print("Startup: telemetry already present, skipping bootstrap")
            return
    except Exception as e:
        print("⚠️  Startup warning: cannot read telemetry collection →", e)
        return

    data_path = Path(__file__).resolve().parents[1] / "data" / "ey_agent_dataset.csv"
    if not data_path.exists():
        print("Startup: CSV not found, skipping bootstrap")
        return

    print("Startup: bootstrapping telemetry from CSV")

    # ---- Load CSV ----
    df = pd.read_csv(data_path)

    # Normalize column names
    cols_lower = {c.lower(): c for c in df.columns}

    vehicle_col = next(
        (v for k, v in cols_lower.items() if "vehicle" in k), None
    )
    timestamp_col = (
        cols_lower.get("timestamp")
        or next((v for k, v in cols_lower.items() if "time" in k), None)
    )

    # ---- Vehicle ID ----
    if vehicle_col:
        df["vehicleId"] = df[vehicle_col].astype(str)
    else:
        df["vehicleId"] = [f"VEH-{i % 10:03d}" for i in range(len(df))]

    # ---- Timestamp ----
    base_time = datetime.utcnow()
    if timestamp_col:
        df["timestamp"] = pd.to_datetime(df[timestamp_col], errors="coerce") \
            .fillna(base_time) \
            .astype(str)
    else:
        df["timestamp"] = [
            (base_time + timedelta(seconds=i)).isoformat()
            for i in range(len(df))
        ]

    # ---- Metadata ----
    df["source"] = "bootstrap_csv"

    # ---- Insert telemetry (cap to avoid overload) ----
    records = df.to_dict(orient="records")
    if not records:
        print("Startup: CSV empty, nothing inserted")
        return

    db.get_collection("telemetry").insert_many(records[:1000])

    # ---- Insert vehicles ----
    vehicles = (
        pd.DataFrame({"vehicleId": df["vehicleId"].unique()})
        .assign(
            timestamp=datetime.utcnow().isoformat(),
            source="bootstrap_csv",
        )
        .to_dict(orient="records")
    )

    if vehicles:
        db.get_collection("vehicles").insert_many(vehicles)

    print(
        f"Startup complete: inserted {min(len(records), 1000)} telemetry records "
        f"and {len(vehicles)} vehicles"
    )

# --------------------------------------------------
# ROUTERS
# --------------------------------------------------

app.include_router(telemetry_api.router, prefix="/api")
app.include_router(prediction_api.router, prefix="/api")
app.include_router(risk_api.router, prefix="/api")
app.include_router(fleet_api.router, prefix="/api")
app.include_router(feedback_api.router, prefix="/api")
app.include_router(alerts_api.router, prefix="/api")
app.include_router(agent_timeline_api.router, prefix="/api")
app.include_router(recommendation_api.router, prefix="/api")
app.include_router(vehicles_api.router, prefix="/api")
app.include_router(assistant_api.router, prefix="/api")
app.include_router(bot_router.router, prefix="/api")


@app.get("/api/assist/breakdown/{vehicleId}")
async def assist_breakdown(vehicleId: str, db=Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Thin wrapper to expose legacy path while delegating logic to bot router implementation
    # Prefer the assistant API compatibility implementation which returns a frontend-friendly shape
    try:
        return await assistant_api.assist_breakdown(vehicleId, db, current_user)
    except Exception:
        # fallback to existing bot implementation if assistant API fails
        return await bot_router.breakdown_assist(vehicleId, db, current_user)

# --------------------------------------------------
# BASIC HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    try:
        db = get_db()
        db.ping_db()
        return {"status": "ok", "db": "connected"}
    except Exception:
        return {"status": "degraded", "db": "unavailable"}
