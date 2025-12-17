import os
import joblib
import json
from typing import Any, List


class ModelLoader:
    """
    Loads the pre-trained model and exposes expected feature ordering.
    Also attempts to load feature medians saved alongside the model.
    """

    def __init__(self) -> None:
        # Resolve model path: check env var first, then try relative from this file's location
        model_path = os.getenv("MODEL_PATH")
        if not model_path:
            # Default: models/ dir at repo root, relative to this file (backend/ml/model_loader.py)
            model_path = os.path.join(os.path.dirname(__file__), "..", "..", "models", "trained_model.pkl")
        
        models_dir = os.path.dirname(model_path)
        medians_path = os.path.join(models_dir, "feature_medians.json")

        self.model = joblib.load(model_path)
        # Prefer feature names recorded by sklearn (convert numpy array to list if needed)
        feature_names = getattr(self.model, "feature_names_in_", None)
        if feature_names is not None:
            self.feature_names: List[str] = list(feature_names)
        else:
            self.feature_names: List[str] = []

        # Fallback to medians file if model doesn't expose feature names
        if not self.feature_names:
            try:
                with open(medians_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    self.feature_names = data.get("expected_features", [])
            except Exception:
                self.feature_names = [f"feature_{i}" for i in range(26)]

    def predict(self, features) -> Any:
        return self.model.predict(features)

    def predict_proba(self, features) -> Any:
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(features)
        # Fallback: use decision_function and squash; simplified for demo use
        preds = self.model.predict(features)
        return [[1 - p, p] for p in preds]

