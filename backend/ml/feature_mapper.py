import pandas as pd
import numpy as np
import json
from typing import List, Dict, Any, Optional


class FeatureMapper:
    """
    Maps arbitrary CSV-derived telemetry rows into the model's expected feature
    vector. The mapper is resilient: it auto-detects numeric columns when
    constructed without explicit expected features, and fills missing values
    with column medians.
    """

    def __init__(self, expected_features: Optional[List[str]] = None) -> None:
        # Coerce numpy arrays or other iterable feature name containers to list
        if expected_features is None:
            self.expected_features = []
        else:
            try:
                self.expected_features = list(expected_features)
            except Exception:
                self.expected_features = []
        self.medians: Dict[str, float] = {feature: 0.0 for feature in self.expected_features}

    def fit_dataframe(self, df: pd.DataFrame) -> None:
        # compute medians from numeric columns present in df
        numeric_df = df.select_dtypes(include=[np.number])
        if not self.expected_features:
            self.expected_features = list(numeric_df.columns)
        self.medians = {}
        for feature in self.expected_features:
            self.medians[feature] = float(numeric_df[feature].median() if feature in numeric_df else 0.0)

    def row_to_features(self, row: Dict[str, Any]) -> np.ndarray:
        feature_vector = []
        for feature in self.expected_features:
            val = row.get(feature)
            if val is None:
                val = self.medians.get(feature, 0.0)
            feature_vector.append(float(val))
        return np.array(feature_vector).reshape(1, -1)

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"expected_features": self.expected_features, "medians": self.medians}, fh)

    @classmethod
    def load(cls, path: str) -> "FeatureMapper":
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        fm = cls(data.get("expected_features", []))
        fm.medians = data.get("medians", {})
        return fm

