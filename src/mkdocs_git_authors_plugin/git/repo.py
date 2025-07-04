import re
from pathlib import Path
from typing import Any, Union, List

from mkdocs_git_authors_plugin.git.command import GitCommand

from mkdocs_git_authors_plugin.git.command import GitCommandError


class Repo(object):
    """
    Abstraction of a Git repository (i.e. the MkDocs project).
    """

    def __init__(self) -> None:
        self._root = self.find_repo_root()
        self._total_lines = 0

        # Store Commit, indexed by 40 char SHA
        self._commits = {}
        # Store Page objects, indexed by Path object
        self._pages = {}
        # Store Author objects, indexed by email
        self._authors = {}

    def add_total_lines(self, cnt: int = 1) -> None:
        """
        Add line(s) to the number of total lines in the repository.

        Args:
            number of lines to add, default: 1
        """
        self._total_lines += cnt

    def author(self, name, email: str):
        """Return an Author object identified by name and email.

        Note: authors are indexed by their email only.
        If no Author object has yet been registered
        a new one is created using name and email.

        Args:
            name: author's full name
            email: author's email address.

        Returns:
            Author object
        """
        if not self._authors.get(email, None):
            from .author import Author

            self._authors[email] = Author(self, name, email)
        return self._authors[email]

    def get_authors(self) -> List[Any]:
        """
        Sorted list of authors in the repository.

        Default sort order is by ascending names,
        and decending when contribution or line count is shown

        Args:

        Returns:
            List of Author objects
        """
        reverse = self.config("show_line_count") or self.config("show_contribution")

        return sorted(
            [author for author in self._authors.values()],
            key=self._sort_key,
            reverse=reverse,
        )

    def config(self, key: str = "") -> Any:
        """
        Return the plugin configuration dictionary or a single config value.

        Args:
            key: lookup key or an empty string.
        """
        return self._config.get(key) if key else self._config

    def find_repo_root(self) -> str:
        """
        Determine the root directory of the Git repository,
        in case the current working directory is different from that.

        Raises a GitCommandError if we're not in a Git repository
        (or Git is not installed).

        Args:

        Returns:
            path as a string
        """
        cmd = GitCommand("rev-parse", ["--show-toplevel"])
        cmd.run()
        stdout = cmd.stdout()
        assert stdout is not None
        return stdout[0]

    def get_commit(self, sha: str, **kwargs) -> Union[Any, None]:
        """
        Return the (cached) Commit object for given sha.

        Implicitly creates a new Commit object upon first request,
        which will trigger the git show processing.

        Args:
            40-byte SHA string

        Returns:
            Commit object
        """
        if not self._commits.get(sha):
            from .commit import Commit

            if self.config("add_co_authors"):
                kwargs["co_authors"] = self._get_co_authors(sha)
            else:
                kwargs["co_authors"] = []
            self._commits[sha] = Commit(self, sha, **kwargs)
        return self._commits.get(sha)

    def _get_co_authors(self, sha) -> List[Any]:
        """
        Execute git log and parse the results.

        This retrieves [co-authors](https://docs.github.com/en/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors) from comment.
        Each line will be associated with a Commit object and counted
        to its co-author's "account".
        Whether empty lines are counted is determined by the
        count_empty_lines configuration option.

        git log -1 <sha> will produce output like the following
        for each line in a file:

        When a commit does not contain co-authors:
            commit ca8b32b24af1ce97fb29c5139b2f80e0c2ad9d1c
            Author: John Doe <jdoe@john.com>
            Date:   Sun Dec 22 11:10:32 2019 +0100

                add plugin skeleton

        When a commit contains co-authors:
            commit ca8b32b24af1ce97fb29c5139b2f80e0c2ad9d1c
            Author: John Doe <jdoe@john.com>
            Date:   Sun Dec 22 11:10:32 2019 +0100

                add plugin skeleton

                Co-authored-by: John Doe <jdoe@john.com>
                Co-authored-by: Rock Smith <rsmith@smith.com>

        In this case we skip the original author as redundant using email address to detect it.

        Args:
            sha: the SHA of the commit to process
            author_email: email of the author
        Returns:
            List of co-authors excluding commit author
        """
        args = ["-1", sha]
        cmd = GitCommand("log", args)
        cmd.run()

        lines = cmd.stdout()

        # in case of empty, non-committed files, raise error
        if len(lines) == 0:
            raise GitCommandError
        co_authors = []

        for line in lines:
            if line.startswith("Author: "):
                # skip author as already available in Commit object
                continue

            result = re.search(r"Co-authored-by: (.*) <(.*)>", line)
            if result is not None and result.group(1) != "" and result.group(2) != "":
                # Extract co-authors from the commit
                co_author = self.author(result.group(1), result.group(2))
                co_authors.append(co_author)
        return co_authors

    def page(self, path):
        """
        Return the (cached) Page object for given path.

        Implicitly creates a new Page object upon first request,
        which will trigger the git blame processing.

        Args:
            path: path (str or Path) to the page's markdown source.

        Returns:
            Page object
        """
        if isinstance(path, str):
            path = Path(path)
        if not self._pages.get(path):
            from .page import Page

            self._pages[path] = Page(self, path, self.config("strict"))
        return self._pages[path]

    def set_config(self, plugin_config) -> None:
        """
        Store the plugin configuration in the Repo instance.

        Args:
            - plugin_config: dictionary
        """
        self._config = plugin_config

    def _sort_key(self, author) -> Any:
        """
        Return a sort key for an author.

        Args:
            author: an Author object

        Returns:
            comparison key for the sorted() function,
        """
        if (
            self.config("show_line_count")
            or self.config("show_contribution")
            or self.config("sort_authors_by") == "contribution"
        ):
            key = "contribution"
        else:
            key = "name"

        func = getattr(author, key)
        return func()

    def total_lines(self):
        """
        The total number of lines in the project's markdown files
        (as counted through git blame).

        Args:

        Returns:
            int total number of lines in the project's markdown files
        """
        return self._total_lines


class AbstractRepoObject(object):
    """
    Base class for objects that live with a repository context.
    """

    def __init__(self, repo: Repo) -> None:
        self._repo = repo

    def repo(self) -> Repo:
        """
        Return a reference to the Repo object.

        Args:

        Returns:
            Repo instance
        """
        return self._repo
