from typing import List, Tuple

import pandas as pd


REQUIRED_COLUMNS = {"vehicleid", "timestamp"}
NUMERIC_BOUNDS = {
    "rpm": (0, 9000),
    "speed": (0, 220),
    "vibration": (0, 5),
    "braking": (0, 1),
}


def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate telemetry CSV contents for required columns and basic sanity.
    This validator is intentionally permissive: it requires only `vehicleId` (or
    `deviceID`) and `timestamp`, and performs numeric sanity checks for any
    recognized numeric columns that are present.
    Returns (is_valid, error_message).
    """
    # Normalize column names to lowercase for consistent checks (in-place)
    df.rename(columns={v: v.lower() for v in df.columns}, inplace=True)

    # Support alias: deviceid -> vehicleid
    if "deviceid" in df.columns and "vehicleid" not in df.columns:
        df["vehicleid"] = df["deviceid"]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        return False, f"Missing required columns: {', '.join(sorted(missing))}"

    # Null checks on required core columns
    for col in REQUIRED_COLUMNS:
        if df[col].isnull().any():
            return False, f"Null values found in column {col}"

    # Basic numeric sanity for known numeric fields if present
    for col, (low, high) in NUMERIC_BOUNDS.items():
        if col in df.columns:
            numeric_series = pd.to_numeric(df[col], errors="coerce")
            if numeric_series.isnull().any():
                return False, f"Non-numeric values found in {col}"
            if (numeric_series < low).any() or (numeric_series > high).any():
                return False, f"Values out of bounds for {col}"

    # Add camelCase aliases expected by ingestion code
    if "vehicleid" in df.columns and "vehicleId" not in df.columns:
        df["vehicleId"] = df["vehicleid"]

    return True, ""

