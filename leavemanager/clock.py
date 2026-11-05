"""Sistem saatine tek erişim noktası (F6): "bugün" Europe/Istanbul takvim günüdür."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Europe/Istanbul")


def today() -> date:
    return datetime.now(TIMEZONE).date()
