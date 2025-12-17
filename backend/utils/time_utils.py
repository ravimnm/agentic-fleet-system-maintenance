from datetime import datetime
from typing import Optional


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def ensure_timestamp(ts: Optional[str]) -> str:
    return ts or now_iso()

