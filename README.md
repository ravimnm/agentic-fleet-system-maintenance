# 🚗 Agentic Fleet Predictive Maintenance System

## Overview

This project is a fleet risk intelligence and predictive maintenance platform combining telemetry ingestion, machine learning, and modular processing architecture.

---

## Architecture

CSV / API → MongoDB → ML Model → Processing Pipeline → FastAPI → React Dashboard

---

## Core Components

### Data Pipeline
- CSV ingestion
- MongoDB collections for telemetry, predictions, risk logs, alerts, and maintenance events

### Processing Pipeline
- Rule evaluation
- ML prediction
- Diagnostics
- Risk scoring
- Scheduling
- Recommendations
- Feedback logging

### Machine Learning
- scikit-learn model
- 26 telemetry features
- Outputs failure probability (0–1)

### API Layer
- FastAPI with modular routes
- RBAC enforcement (basic)

### Frontend
- React + Vite + Tailwind
- Dashboard, analytics, alerts, audit logs

---

## Setup

### Backend
cd backend  
pip install -r requirements.txt  
uvicorn main:app --reload  

### Frontend
cd frontend  
npm install  
npm run dev  

---

## Limitations

- Deterministic pipeline (not autonomous)
- No event-driven processing
- No real-time streaming
- Basic authentication

---

## Future Work

- Agent planning layer
- Event-driven architecture
- Real-time ingestion
- Strong authentication

---

## Summary

A production-style prototype demonstrating backend engineering, ML integration, and system design for fleet maintenance.
