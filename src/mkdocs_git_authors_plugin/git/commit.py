import re
from typing import Any, Union, List

from mkdocs_git_authors_plugin import util
from mkdocs_git_authors_plugin.git.repo import AbstractRepoObject, Repo


class Commit(AbstractRepoObject):
    """
    Information about a single commit.

    Stores only information relevant to our plugin:
    - author name and email,
    - date/time
    - summary (not used at this point)
    """

    def __init__(
        self,
        repo: Repo,
        sha: str,
        author_name: str,
        author_email: str,
        author_time: str,
        author_tz: str,
        summary: str,
        co_authors: List[Any],
    ):
        """Initialize a commit from its SHA.

        Populates the object running git show.

        Args:
            repo: reference to the Repo instance
            sha: 40-byte SHA string
        """

        super().__init__(repo)

        # Replace <>
        # from '<email@domain.com>'
        # to   'email@domain.com'
        author_email = re.sub(r"\<|\>", "", author_email)
        # Lowercase, as emails are not case sensitive.
        # See https://github.com/timvink/mkdocs-git-authors-plugin/issues/59
        author_email = author_email.lower()

        self._author = self.repo().author(author_name, author_email)
        self._datetime = util.commit_datetime(author_time, author_tz)
        self._datetime_string = util.commit_datetime_string(self._datetime)
        self._summary = summary
        self._co_authors = co_authors

    def author(self):
        """
        The commit's author.

        Args:

        Returns:
            Author object
        """
        return self._author

    def co_authors(self):
        """
        The commit's co-author.

        Args:

        Returns:
            Co-Authors list
        """
        return self._co_authors

    def datetime(self, _type=str) -> Union[str, util.datetime]:
        """
        The commit's commit time.

        Stored as a datetime.datetime object with timezone information.

        Args:
            _type: str or other type expression

        Returns:
            The commit's commit time, either as a formatted string (_type=str)
            or as a datetime.datetime expression with tzinfo
        """
        return self._datetime_string if _type is str else self._datetime
