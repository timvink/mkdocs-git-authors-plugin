from datetime import datetime, timezone, timedelta

def commit_datetime(dt: str):
    """
    Convert a commit's datetime string to a
    datetime.datetime object with timezone info.

    Args:
        A string returned from the %ai formatting argument
        in a git show command.

    Returns:
        datetime.datetime object with tzinfo
    """
    d, t, tz = dt.split(' ')
    d = [int(v) for v in d.split('-')]
    t = [int(v) for v in t.split(':')]
    # timezone info looks like +hhmm or -hhmm
    tz_hours = int(tz[:3])
    th_minutes = int(tz[0] + tz[3:])

    # Construct 'aware' datetime.datetime object
    return datetime(
        d[0], d[1], d[2],
        hour=t[0],
        minute=t[1],
        second=t[2],
        tzinfo=timezone(timedelta(hours=tz_hours,minutes=th_minutes))
    )
