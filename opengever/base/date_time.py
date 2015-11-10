from datetime import datetime
import pytz


def utcnow_tz_aware():
    """Returns the utc now datetime timezone aware."""
    return datetime.now(pytz.UTC)


def as_utc(aware_dt):
    """Convert timezone aware datetime to UTC timezone."""

    return pytz.UTC.normalize(aware_dt.astimezone(pytz.UTC))
