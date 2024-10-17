from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from mkdocs_git_authors_plugin.config import GitAuthorsPluginConfig


def commit_datetime(author_time: str, author_tz: str) -> datetime:
    """
    Convert a commit's timestamp to an aware datetime object.

    Args:
        author_time: Unix timestamp string
        author_tz: string in the format +hhmm

    Returns:
        datetime.datetime object with tzinfo
    """

    # timezone info looks like +hhmm or -hhmm
    tz_hours = int(author_tz[:3])
    th_minutes = int(author_tz[0] + author_tz[3:])

    return datetime.fromtimestamp(
        int(author_time), timezone(timedelta(hours=tz_hours, minutes=th_minutes))
    )


def commit_datetime_string(dt: datetime) -> str:
    """
    Return a string representation for a commit's timestamp.

    Args:
        dt: datetime object with tzinfo

    Returns:
        string representation (should be localized)
    """
    return dt.strftime("%c %z")


def page_authors_summary(page, config: dict) -> str:
    """
    A summary of the authors' contributions on a page level

    Args:
        page (Page): Page class
        config (dict): plugin's config dict

    Returns:
        str: HTML text with authors
    """

    authors = page.get_authors()
    authors_summary = []
    author_name = ""

    for author in authors:
        contrib = (
            f" ({author.contribution(page.path(), str)})"
            if page.repo().config("show_contribution") and len(page.get_authors()) > 1
            else ""
        )
        if page.repo().config("show_email_address"):
            href = (
                page.repo()
                .config("href")
                .format(email=author.email(), name=author.name())
            )
            author_name = f"<a href='{href}'>{author.name()}</a>"
        else:
            author_name = author.name()
        authors_summary.append(f"{author_name}{contrib}")

    authors_summary_str = ", ".join(authors_summary)
    return f"<span class='git-page-authors git-authors'>{authors_summary_str}</span>"


def site_authors_summary(authors, config: GitAuthorsPluginConfig) -> str:
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
    result = """
<span class='git-authors'>
    <ul>
        """
    for author in authors:
        contribution = (
            f" ({author.contribution(None, str)})" if config.show_contribution else ""
        )
        lines = f": {author.lines()} lines" if config.show_line_count else ""
        author_name = ""
        if config.show_email_address:
            href = config["href"].format(email=author.email(), name=author.name())
            author_name = f'<a href="{href}">{author.name()}</a>'
        else:
            author_name = author.name()
        result += """
    <li>{author_name}{lines}{contribution}</li>
    """.format(
            author_name=author_name,
            lines=lines,
            contribution=contribution,
        )
    result += """
    </span>
</ul>
    """
    return result


def page_authors(authors: List, path: str) -> List[Dict[str, Any]]:
    """List of dicts with info on page authors
    # TODO: rename to something more representative like 'authors_to_dict()'
    Args:
        authors (list): list with Author classes
        path (str): path to page
    """
    if isinstance(path, str):
        path = Path(path)
    return [
        {
            "name": author.name(),
            "email": author.email(),
            "last_datetime": author.datetime(path, str),
            "lines": author.lines(path),
            "lines_all_pages": author.lines(),
            "contribution": author.contribution(path, str),
            "contribution_all_pages": author.contribution(None, str),
        }
        for author in authors
    ]
