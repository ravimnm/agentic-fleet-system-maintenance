from datetime import datetime
from typing import Dict, Any

from ml.model_loader import ModelLoader
from ml.feature_mapper import FeatureMapper
from ml.predictor import PredictorService
from database.mongo_client import MongoConnection
from utils.explainability import explain


class PredictionAgent:
    def __init__(self, db: MongoConnection) -> None:
        self.db = db
        self.model_loader = ModelLoader()
        self.feature_mapper = FeatureMapper(self.model_loader.feature_names)
        # Fit medians lazily from latest telemetry if available
        telemetry_docs = self.db.find_many("telemetry", {}, limit=500)
        if telemetry_docs:
            import pandas as pd

            df = pd.DataFrame(telemetry_docs)
            self.feature_mapper.fit_dataframe(df)
        self.predictor = PredictorService(self.model_loader, self.feature_mapper)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        telemetry = context["telemetry"]
        result = self.predictor.predict_row(telemetry)
        explanation_details = self._build_explanation_details(telemetry)
        doc = {
            **result,
            "vehicleId": telemetry.get("vehicleId"),
            "timestamp": telemetry.get("timestamp", datetime.utcnow().isoformat()),
            "source": "PredictionAgent",
            "explanation_text": result.get("explanation"),
            "explanation": explanation_details,
        }
        self.db.insert("predictions", doc)
        self.db.insert(
            "agent_actions",
            {
                "vehicleId": doc["vehicleId"],
                "timestamp": doc["timestamp"],
                "source": "PredictionAgent",
                "action": "Predicted event",
                "reason": ", ".join(
                    f"{item['feature']} ({item['impact']})" for item in explanation_details
                )
                if explanation_details
                else result.get("explanation", ""),
            },
        )
        return doc

    def _build_explanation_details(self, telemetry: Dict[str, Any]):
        feature_names = self.model_loader.feature_names
        feature_map = {name: telemetry.get(name, 0) for name in feature_names}

        weights = {}
        model = getattr(self.model_loader, "model", None)
        if model is not None:
            if hasattr(model, "coef_"):
                try:
                    coef = model.coef_[0]
                    weights = {name: coef[idx] for idx, name in enumerate(feature_names)}
                except Exception:
                    weights = {}
            elif hasattr(model, "feature_importances_"):
                try:
                    imp = model.feature_importances_
                    weights = {name: imp[idx] for idx, name in enumerate(feature_names)}
                except Exception:
                    weights = {}

        return explain(feature_map, weights)

