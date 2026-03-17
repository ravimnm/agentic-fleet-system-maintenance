Agentic Fleet Predictive Maintenance System
Overview

This project is a fleet risk intelligence and predictive maintenance platform that combines:

telemetry ingestion

machine learning-based failure prediction

rule-based diagnostics

modular agent-style processing

full-stack visualization

It is designed as a production-style prototype demonstrating backend architecture, ML integration, and decision workflows for fleet operations.

Architecture
CSV / API Input
        ↓
   MongoDB (Telemetry Storage)
        ↓
   ML Prediction Layer
        ↓
   Processing Pipeline (Agent Modules)
        ↓
   FastAPI Backend (RBAC APIs)
        ↓
   React Dashboard
Core Components
1. Data Pipeline

CSV telemetry ingestion

MongoDB collections:

vehicles

telemetry

predictions

risk_logs

maintenance_events

alerts

agent_actions

feedback

2. Processing Pipeline (Agent Modules)

The system uses modular processing units (referred to as agents) coordinated by a central orchestrator.

Execution Flow
Telemetry Input
   ↓
Rule Evaluation
   ↓
ML Prediction
   ↓
Diagnostics
   ↓
Risk Scoring
   ↓
Maintenance Scheduling
   ↓
Recommendations
   ↓
Feedback Logging
Modules

RuleAgent → detects rule-based anomalies

PredictionAgent → ML inference (failure probability)

DiagnosticsAgent → analyzes telemetry patterns

RiskAgent → computes overall risk score

SchedulingAgent → generates maintenance plans

RecommendationAgent → suggests actions

FeedbackAgent → captures operator input

Note: Current system uses deterministic orchestration, not autonomous planning.

3. Machine Learning

Model: scikit-learn (joblib)

Input: 26 telemetry features

Output:

failure probability (0–1)

predicted event type

Features include:

engine RPM

coolant temperature

oil pressure

battery voltage

vehicle speed

braking behavior

tire pressure

fuel consumption

Data Handling

Missing values → median imputation

Automatic numeric feature detection

4. API Layer (FastAPI)
Key Endpoints
POST   /api/telemetry/ingest
GET    /api/telemetry/latest/{vehicleId}
POST   /api/predict
GET    /api/predict/{vehicleId}
GET    /api/risk/{vehicleId}
GET    /api/fleet/overview
GET    /api/fleet/top-risk
GET    /api/fleet/agent-actions
POST   /api/feedback
POST   /api/bot/chat
GET    /api/assist/breakdown/{vehicleId}
GET    /api/alerts
Features

dependency injection (FastAPI)

modular routing

basic RBAC enforcement

5. Frontend (React + Vite)
Pages

Fleet Dashboard (admin)

Vehicle Analytics (user)

Risk Analytics

Alerts Management

Agent Timeline (audit logs)

Breakdown Assistance

Features

role-based UI filtering

charts (Recharts)

explainability panels

assistant widget

6. Breakdown Assistance

Triggered when:

risk > 0.8 OR failure_probability > 0.85

Provides:

nearest service center (Haversine distance)

highest-rated center

contact + navigation options

7. Audit & Explainability

All system actions are logged:

agent_actions collection

Each record includes:

agent name

decision

reasoning

timestamp

Technology Stack
Layer	Technology
Frontend	React, Vite, Tailwind CSS
Backend	FastAPI, Python
Database	MongoDB
ML	scikit-learn, Pandas
Visualization	Recharts
Auth	Mock RBAC (localStorage + API checks)
Project Structure
backend/
  agents/
  api/
  database/
  ml/
  utils/
  scripts/

frontend/
  src/
    components/
    pages/
    context/
    api/

models/
data/
Setup
Prerequisites

Python 3.10+

Node.js 18+

MongoDB running locally

Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
Frontend
cd frontend
npm install
npm run dev
Access
http://localhost:5173
Design Principles

modular architecture (SRP)

separation of ML and API layers

auditability of decisions

explainable outputs

scalable backend structure

Current Limitations

This is a deterministic pipeline, not a fully autonomous agent system.

Limitations:

no dynamic planning or tool selection

no feedback loop / iterative reasoning

no event-driven architecture (batch/request-based)

no real-time streaming (Kafka, MQTT, etc.)

basic RBAC (no JWT / auth server)

Future Improvements

introduce planner + tool abstraction

event-driven ingestion (Kafka / Redis streams)

real-time telemetry processing

feedback loop for post-maintenance evaluation

stronger authentication (JWT / OAuth)

model retraining pipeline

Purpose

This project demonstrates:

backend system design

ML integration in production-style pipelines

modular processing architecture

full-stack engineering capability

Summary

This is a well-structured predictive maintenance system with:

strong backend foundations

integrated ML pipeline

clear system observability

practical fleet use case

It is not yet a true autonomous agent system, but provides a solid base to evolve into one.
