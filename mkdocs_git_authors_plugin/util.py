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


def repo_authors_summary(authors, config: dict):
    """
    A summary list of the authors' contributions on repo level.

    Iterates over all authors and produces an HTML <ul> list with
    their names and overall contribution details (lines/percentage).

    TODO:
    - The output should be configurable or at least localizable
        (suggestions:
        - load a template with named fields for the values
            (user may provide alternative template)
        - provide plugin configuration options for the various labels
        )

    Args:
        authors: sorted list of Author objects
        config: plugin's config dict

    Returns:
        Unordered HTML list as a string.
    """
    show_contribution = config['show_contribution']
    show_line_count = show_contribution and config['show_line_count']
    result = """
<span class='git-authors'>
    <ul>
        """
    for author in authors:
        contribution = (
            ' (%s)' % author.contribution(None, str)
            if show_contribution
            else ''
        )
        lines = (
            '%s lines' % author.lines()
            if show_line_count
            else ''
        )
        result += """
    <li><a href='mailto:{author_email}'>{author_name}</a>:
    {lines}{contribution}</li>
    """.format(
        author_email=author.email(),
        author_name=author.name(),
        lines=lines,
        contribution=contribution
    )
    result += """
    </span>
</ul>
    """
    return result
