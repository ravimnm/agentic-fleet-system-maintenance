from typing import Dict, Any, List
from database.mongo_client import MongoConnection
from agents.prediction_agent import PredictionAgent
from agents.diagnostics_agent import DiagnosticsAgent
from agents.risk_agent import RiskAgent
from agents.scheduling_agent import SchedulingAgent
from agents.feedback_agent import FeedbackAgent
from agents.rule_agent import RuleAgent
from agents.recommendation_agent import RecommendationAgent
from utils.agent_logger import log_timeline_entry


class MasterAgent:
    def __init__(self, db: MongoConnection) -> None:
        self.db = db
        self.prediction_agent = PredictionAgent(db)
        self.diagnostics_agent = DiagnosticsAgent(db)
        self.risk_agent = RiskAgent(db)
        self.scheduling_agent = SchedulingAgent(db)
        self.feedback_agent = FeedbackAgent(db)
        self.rule_agent = RuleAgent(db)
        self.recommendation_agent = RecommendationAgent(db)

    def process_telemetry(self, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        context: Dict[str, Any] = {"telemetry": telemetry}

        rule_alerts = self.rule_agent.handle(context)
        for alert in rule_alerts:
            log_timeline_entry(
                self.db,
                telemetry.get("vehicleId"),
                "RuleAgent",
                f"Rule triggered ({alert.get('rule')}) with severity {alert.get('severity')}",
                alert.get("timestamp"),
                {"details": alert.get("details")},
            )

        prediction = self.prediction_agent.handle(context)
        log_timeline_entry(
            self.db,
            telemetry.get("vehicleId"),
            "PredictionAgent",
            f"Predicted {prediction.get('predicted_event')} ({prediction.get('probability', 0):.2f})",
            prediction.get("timestamp"),
        )

        diagnostics = self.diagnostics_agent.handle(context, prediction)
        log_timeline_entry(
            self.db,
            telemetry.get("vehicleId"),
            "DiagnosticsAgent",
            diagnostics.get("summary", "Diagnostics completed"),
            diagnostics.get("timestamp"),
        )

        risk = self.risk_agent.handle(context, prediction, diagnostics)
        log_timeline_entry(
            self.db,
            telemetry.get("vehicleId"),
            "RiskAgent",
            f"Risk classified {risk.get('category')} ({risk.get('risk_score', 0):.2f})",
            risk.get("timestamp"),
        )

        recommendations = self.recommendation_agent.handle(context, risk, diagnostics)
        for rec in recommendations:
            log_timeline_entry(
                self.db,
                telemetry.get("vehicleId"),
                "RecommendationAgent",
                f"{rec.get('component')} -> {rec.get('recommendation')}",
                rec.get("timestamp"),
                {"severity": rec.get("severity")},
            )

        schedule = self.scheduling_agent.handle(context, prediction, risk)
        feedback = self.feedback_agent.handle(context, prediction, risk)

        self._update_vehicle_health(telemetry, prediction, risk)

        return {
            "prediction": prediction,
            "diagnostics": diagnostics,
            "risk": risk,
            "schedule": schedule,
            "feedback": feedback,
            "alerts": rule_alerts,
            "recommendations": recommendations,
        }

    def log_action(self, action: Dict[str, Any]) -> None:
        self.db.insert("agent_actions", action)

    def _update_vehicle_health(
        self, telemetry: Dict[str, Any], prediction: Dict[str, Any], risk: Dict[str, Any]
    ) -> None:
        vehicle_id = telemetry.get("vehicleId")
        probability = prediction.get("probability", 0.0)
        risk_score = risk.get("risk_score", 0.0)

        if risk_score > 0.8:
            health_state = "grounded"
        elif probability > 0.75:
            health_state = "critical"
        elif risk_score >= 0.4 or probability > 0.5:
            health_state = "warning"
        else:
            health_state = "healthy"

        update_doc = {
            "$set": {
                "healthState": health_state,
                "timestamp": telemetry.get("timestamp"),
            }
        }
        self.db.upsert_one("vehicles", {"vehicleId": vehicle_id}, update_doc)
        log_timeline_entry(
            self.db,
            vehicle_id,
            "MasterAgent",
            f"Health state set to {health_state}",
            telemetry.get("timestamp"),
        )

