from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

TEHRAN_TZ = ZoneInfo("Asia/Tehran")

def ensure_utc_aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    # اگر naive بود، در پروژه فعلی عملاً UTC است (چون utcnow استفاده شده)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    # اگر aware بود، به UTC نرمال کن
    return dt.astimezone(timezone.utc)

def to_tehran(dt: datetime | None) -> datetime | None:
    dt_utc = ensure_utc_aware(dt)
    if dt_utc is None:
        return None
    return dt_utc.astimezone(TEHRAN_TZ)
