from datetime import datetime, timedelta, timezone
from enum import Enum


class TimeRangePreset(str, Enum):
    """Time ranges"""

    LAST_7_DAYS = "last_7_days"
    LAST_30_DAYS = "last_30_days"
    LAST_90_DAYS = "last_90_days"
    THIS_WEEK = "this_week"
    THIS_MONTH = "this_month"
    THIS_YEAR = "this_year"
    YESTERDAY = "yesterday"
    TODAY = "today"


class TimeRange:
    def __init__(self, start: datetime | None = None, end: datetime | None = None):
        self.start = start
        self.end = end

    @classmethod
    def from_preset(cls, preset: TimeRangePreset) -> "TimeRange":
        """Create a time range from preset"""
        now = datetime.now(timezone.utc)

        if preset == TimeRangePreset.LAST_7_DAYS:
            return cls(start=now - timedelta(days=7), end=now)

        elif preset == TimeRangePreset.LAST_30_DAYS:
            return cls(start=now - timedelta(days=30), end=now)

        elif preset == TimeRangePreset.LAST_90_DAYS:
            return cls(start=now - timedelta(days=90), end=now)

        elif preset == TimeRangePreset.TODAY:
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return cls(start=start_of_day, end=now)

        elif preset == TimeRangePreset.YESTERDAY:
            yesterday = now - timedelta(days=1)
            start_of_yesterday = yesterday.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            end_of_yesterday = start_of_yesterday + timedelta(days=1)
            return cls(start=start_of_yesterday, end=end_of_yesterday)

        elif preset == TimeRangePreset.THIS_WEEK:
            # Понеділок поточного тижня
            start_of_week = now - timedelta(days=now.weekday())
            start_of_week = start_of_week.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            return cls(start=start_of_week, end=now)

        elif preset == TimeRangePreset.THIS_MONTH:
            start_of_month = now.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            return cls(start=start_of_month, end=now)

        elif preset == TimeRangePreset.THIS_YEAR:
            start_of_year = now.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
            return cls(start=start_of_year, end=now)

        return cls()

    @classmethod
    def last_n_days(cls, days: int) -> "TimeRange":
        now = datetime.now(timezone.utc)
        return cls(start=now - timedelta(days=days), end=now)

    @classmethod
    def last_n_hours(cls, hours: int) -> "TimeRange":
        now = datetime.now(timezone.utc)
        return cls(start=now - timedelta(hours=hours), end=now)

    @classmethod
    def custom(
        cls, start: datetime | None = None, end: datetime | None = None
    ) -> "TimeRange":
        """Custom range"""
        return cls(start=start, end=end)

    def __repr__(self) -> str:
        return f"TimeRange(start={self.start}, end={self.end})"
