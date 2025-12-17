from typing import Dict, Any

import numpy as np

from .model_loader import ModelLoader
from .feature_mapper import FeatureMapper


class PredictorService:
    def __init__(self, model_loader: ModelLoader, feature_mapper: FeatureMapper) -> None:
        self.model_loader = model_loader
        self.feature_mapper = feature_mapper

    def predict_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        features = self.feature_mapper.row_to_features(row)
        proba = self.model_loader.predict_proba(features)[0]
        predicted = self.model_loader.predict(features)[0]
        explanation = self._build_explanation(features[0])
        return {
            "probability": float(np.max(proba)),
            "predicted_event": str(predicted),
            "explanation": explanation,
        }

    def _build_explanation(self, feature_vector) -> str:
        # Simple explanation using top contributing features
        top_indices = np.argsort(np.abs(feature_vector))[-3:][::-1]
        top_feats = [self.feature_mapper.expected_features[i] for i in top_indices]
        return f"Top signals: {', '.join(top_feats)} drove this prediction."

