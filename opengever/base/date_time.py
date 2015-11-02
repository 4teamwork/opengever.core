from datetime import datetime
import pytz


def utcnow_tz_aware():
    """Returns the utc now datetime timezone aware."""
    return datetime.now(pytz.utc)
