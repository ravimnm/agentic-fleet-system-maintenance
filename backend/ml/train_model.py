import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
from .feature_mapper import FeatureMapper

# -----------------------------
# CONFIG
# -----------------------------
CSV_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'ey_agent_dataset.csv')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
MODEL_FILE = os.path.join(MODEL_DIR, 'trained_model.pkl')
MEDIANS_FILE = os.path.join(MODEL_DIR, 'feature_medians.json')

# Target column (adjust if your CSV label column has a different name)
TARGET_COL = 'event'  # e.g., Normal / Sharp Turn / Hard Brake

# -----------------------------
# 1. LOAD DATA
# -----------------------------
df = pd.read_csv(CSV_FILE)

# Drop obvious non-feature metadata
drop_cols = [c for c in ['tripID', 'deviceID', 'timeStamp', 'event'] if c in df.columns]
features_df = df.drop(columns=drop_cols)
# Select numeric columns only (these become model features)
features_df = features_df.select_dtypes(include=[np.number])

# Prepare target
y = df[TARGET_COL].values

# -----------------------------
# 2. BUILD FEATURE MAPPER
# -----------------------------
feature_names = list(features_df.columns)
fm = FeatureMapper(feature_names)
fm.fit_dataframe(features_df)

# ensure models dir exists
os.makedirs(MODEL_DIR, exist_ok=True)
fm.save(MEDIANS_FILE)
print(f"Saved feature medians to {MEDIANS_FILE}")

# -----------------------------
# 3. TRAIN/TEST SPLIT
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    features_df, y, test_size=0.2, random_state=42, stratify=y
)

# -----------------------------
# 4. TRAIN MODEL (using DataFrame so sklearn records feature names)
# -----------------------------
clf = RandomForestClassifier(
    n_estimators=100,
    max_depth=None,
    random_state=42,
    n_jobs=-1
)
clf.fit(X_train, y_train)

# -----------------------------
# 5. EVALUATE
# -----------------------------
y_pred = clf.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# -----------------------------
# 6. SAVE MODEL
# -----------------------------
joblib.dump(clf, MODEL_FILE)
print(f"Model trained and saved to {MODEL_FILE}")
