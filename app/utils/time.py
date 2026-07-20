from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

TEHRAN = ZoneInfo("Asia/Tehran")

def as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        # داده‌های فعلی شما عملاً UTC هستند (چون utcnow استفاده شده)
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def to_tehran_iso(dt: datetime | None) -> str | None:
    dt = as_utc(dt)
    if dt is None:
        return None
    return dt.astimezone(TEHRAN).isoformat()
