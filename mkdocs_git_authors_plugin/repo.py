from pathlib import Path
import logging
import os
import re
import subprocess

from . import util

class GitCommandError(Exception):
    """
    Exception thrown by a GitCommand.
    """
    pass


class GitCommand(object):
    """
    Wrapper around a Git command.

    Instantiate with a command name and an optional args list.
    These can later be modified with set_command() and set_args().

    Execute the command with run()

    If successful the results can be read as string lists with
    - stdout()
    - stderr()
    In case of an error a verbose GitCommandError is raised.
    """

    def __init__(self, command: str, args: list = []):
        """
        Initialize the GitCommand.

        Args:
            command a string ('git' will implicitly be prepended)
            args: a string list with remaining command arguments.
                  Defaults to an empty list
        """

        self.set_command(command)
        self.set_args(args)
        self._stdout = None
        self._stderr = None
        self._completed = False

    def run(self):
        """
        Execute the configured Git command.

        In case of success the results can be retrieved as string lists
        with self.stdout() and self.stderr(), otherwise a GitCommandError
        is raised.

        Args:

        Returns:
            The process's return code.
                Note: usually the result will be used through the methods.
        """

        args = ['git']
        args.append(self._command)
        args.extend(self._args)
        p = subprocess.run(
            args,
            encoding='utf8',
            capture_output=True
        )
        try:
            p.check_returncode()
        except subprocess.CalledProcessError as e:
            msg = ['GitCommand error:']
            msg.append('Command "%s" failed' % ' '.join(args))
            msg.append('Return code: %s' % p.returncode)
            msg.append('Output:')
            msg.append(p.stdout)
            msg.append('Error messages:')
            msg.append(p.stderr)
            raise GitCommandError('\n'.join(msg))

        self._stdout = p.stdout.strip('\'\n').split('\n')
        self._stderr = p.stderr.strip('\'\n').split('\n')

        self._completed = True
        return p.returncode

    def set_args(self, args: list):
        """
        Change the command arguments.

        Args:
            args: list of process arguments
        """
        self._args = args

    def set_command(self, command: str):
        """
        Change the Git command.

        Args:
            command: string with the git-NNN command name.
        """
        self._command = command

    def stderr(self):
        """
        Return the stderr output of the command as a string list.

        Args:

        Returns:
            string list
        """
        if not self._completed:
            raise GitCommandError('Trying to read from uncompleted GitCommand')
        return self._stderr

    def stdout(self):
        """
        Return the stdout output of the command as a string list.

        Args:

        Returns:
            string list
        """
        if not self._completed:
            raise GitCommandError('Trying to read from uncompleted GitCommand')
        return self._stdout


class Repo(object):
    """
    Abstraction of a Git repository (i.e. the MkDocs project).
    """

    def __init__(self):
        self._root = self.find_repo_root()
        self._total_lines = 0

        # Store Commit, indexed by 40 char SHA
        self._commits = {}
        # Store Page objects, indexed by Path object
        self._pages = {}
        # Store Author objects, indexed by email
        self._authors = {}

    def add_total_lines(self, cnt: int = 1):
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
            self._authors[email] = Author(self, name, email)
        return self._authors[email]

    def get_authors(self):
        """
        Sorted list of authors in the repository.

        Default sort order is by ascending names, which can be changed
        to descending and/or by contribution

        Args:

        Returns:
            List of Author objects
        """
        return sorted([
                author for author in self._authors.values()
            ],
            key=self._sort_key,
            reverse=self.config('sort_reverse')
        )

    def config(self, key: str = ''):
        """
        Return the plugin configuration dictionary or a single config value.

        Args:
            key: lookup key or an empty string.
        """
        return self._config.get(key) if key else self._config

    def find_repo_root(self):
        """
        Determine the root directory of the Git repository,
        in case the current working directory is different from that.

        Raises a GitCommandError if we're not in a Git repository
        (or Git is not installed).

        Args:

        Returns:
            path as a string
        """
        cmd = GitCommand('rev-parse', ['--show-toplevel'])
        cmd.run()
        return cmd.stdout()[0]

    def get_commit(self, sha: str, **kwargs):
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
            self._commits[sha] = Commit(self, sha, **kwargs)
        return self._commits.get(sha)

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
        if type(path) == str:
            path = Path(path)
        if not self._pages.get(path):
            self._pages[path] = Page(self, path)
        return self._pages[path]

    def set_config(self, plugin_config):
        """
        Store the plugin configuration in the Repo instance.

        Args:
            - plugin_config: dictionary
        """
        self._config = plugin_config

    def _sort_key(self, author):
        """
        Return a sort key for an author.

        Args:
            author: an Author object

        Returns:
            comparison key for the sorted() function,
            determined by the 'sort_authors_by' configuration option
        """
        func = getattr(author, self.config('sort_authors_by'))
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

    def __init__(self, repo: Repo):
        self._repo = repo

    def repo(self):
        """
        Return a reference to the Repo object.

        Args:

        Returns:
            Repo instance
        """
        return self._repo


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
        summary: str
    ):
        """Initialize a commit from its SHA.

        Populates the object running git show.

        Args:
            repo: reference to the Repo instance
            sha: 40-byte SHA string
        """

        super().__init__(repo)

        self._author = self.repo().author(
            author_name,
            author_email
        )
        self._datetime = util.commit_datetime(author_time, author_tz)
        self._datetime_string = util.commit_datetime_string(self._datetime)
        self._summary = summary

    def author(self):
        """
        The commit's author.

        Args:

        Returns:
            Author object
        """
        return self._author

    def datetime(self, _type=str):
        """
        The commit's commit time.

        Stored as a datetime.datetime object with timezone information.

        Args:
            _type: str or other type expression

        Returns:
            The commit's commit time, either as a formatted string (_type=str)
            or as a datetime.datetime expression with tzinfo
        """
        return self._datetime_string if _type == str else self._datetime


class Page(AbstractRepoObject):
    """
    Results of git blame for a given file.

    Stores a list of tuples with a reference to a
    Commit object and a list of consecutive lines
    modified by that commit.
    """

    def __init__(self, repo: Repo, path: Path):
        """
        Instantiante a Page object

        Args:
            repo: Reference to the global Repo instance
            path: Absolute path to the page's Markdown file
        """
        super().__init__(repo)
        self._path = path
        self._sorted = False
        self._total_lines = 0
        self._authors = []
        try:
            self._process_git_blame()
        except GitCommandError:
            logging.warning(
                '%s has not been committed yet. Lines are not counted' % path
            )

    def add_total_lines(self, cnt: int = 1):
        """
        Add line(s) to the count of total lines for the page.

        Arg:
            cnt: number of lines to add. Default: 1
        """
        self._total_lines += cnt

    def get_authors(self):
        """
        Return a sorted list of authors for the page

        The list is sorted once upon first request.
        Sorting is done by author name.

        Args:

        Returns:
            sorted list with Author objects
        """
        if not self._sorted:
            repo = self.repo()
            self._authors = sorted(
                self._authors,
                key=repo._sort_key,
                reverse=repo.config('sort_reverse')
            )
            self._sorted = True
        return self._authors

    def authors_summary(self):
        """
        Summarized list of authors to a HTML string

        Args:
        Returns:
            str: HTML text with authors
        """

        authors = self.get_authors()
        authors_summary = []
        for author in authors:
            contrib = (
                ' (%s)' % author.contribution(self.path(), str)
                if self.repo().config('show_contribution')
                and len(self.get_authors()) > 1
                else ''
            )
            authors_summary.append(
                "<a href='mailto:%s'>%s</a>%s" % (
                    author.email(),
                    author.name(),
                    contrib
                ))
        authors_summary = ', '.join(authors_summary)
        return "<span class='git-authors'>%s</span>" % authors_summary

    def _process_git_blame(self):
        """
        Execute git blame and parse the results.

        This retrieves all data we need, also for the Commit object.
        Each line will be associated with a Commit object and counted
        to its author's "account".
        Whether empty lines are counted is determined by the
        count_empty_lines configuration option.

        git blame --porcelain will produce output like the following
        for each line in a file:

        When a commit is first seen in that file:
            30ed8daf1c48e4a7302de23b6ed262ab13122d31 1 2 1
            author John Doe
            author-mail <j.doe@example.com>
            author-time 1580742131
            author-tz +0100
            committer John Doe
            committer-mail <j.doe@example.com>
            committer-time 1580742131
            summary Fancy commit message title
            filename home/docs/README.md
                    line content (indicated by TAB. May be empty after that)

        When a commit has already been seen *in that file*:
            82a3e5021b7131e31fc5b110194a77ebee907955 4 5
                    line content

        In this case the metadata is not repeated, but it is guaranteed that
        a Commit object with that SHA has already been created so we don't
        need that information anymore.

        When a line has not been committed yet:
            0000000000000000000000000000000000000000 1 1 1
            author Not Committed Yet
            author-mail <not.committed.yet>
            author-time 1583342617
            author-tz +0100
            committer Not Committed Yet
            committer-mail <not.committed.yet>
            committer-time 1583342617
            committer-tz +0100
            summary Version of books/main/docs/index.md from books/main/docs/index.md
            previous 1f0c3455841488fe0f010e5f56226026b5c5d0b3 books/main/docs/index.md
            filename books/main/docs/index.md
                    uncommitted line content

        In this case exactly one Commit object with the special SHA and fake
        author will be created and counted.

        Args:
            ---
        Returns:
            --- (this method works through side effects)
        """

        re_sha = re.compile('^\w{40}')

        cmd = GitCommand('blame', ['--porcelain', str(self._path)])
        cmd.run()

        commit_data = {}
        for line in cmd.stdout():
            key = line.split(' ')[0]
            m = re_sha.match(key)
            if m:
                commit_data = {
                    'sha': key
                }
            elif key in [
                'author',
                'author-mail',
                'author-time',
                'author-tz',
                'summary'
            ]:
                commit_data[key] = line[len(key)+1:]
            elif line.startswith('\t'):
                # assign the line to a commit
                # and create the Commit object if necessary
                commit = self.repo().get_commit(
                    commit_data.get('sha'),
                    # The following values are guaranteed to be present
                    # when a commit is seen for the first time,
                    # so they can be used for creating a Commit object.
                    author_name=commit_data.get('author'),
                    author_email=commit_data.get('author-mail'),
                    author_time=commit_data.get('author-time'),
                    author_tz=commit_data.get('author-tz'),
                    summary=commit_data.get('summary')
                )
                if len(line) > 1 or self.repo().config('count_empty_lines'):
                    author = commit.author()
                    if author not in self._authors:
                        self._authors.append(author)
                    author.add_lines(self, commit)
                    self.add_total_lines()
                    self.repo().add_total_lines()

    def path(self):
        """
        The path to the markdown file.

        Args:

        Returns:
            Absolute path as Path object.
        """
        return self._path

    def total_lines(self):
        """
        Total number of lines in the markdown source file.

        Args:

        Returns:
            int
        """
        return self._total_lines


class Author(AbstractRepoObject):
# Sorted after Page for the function annotations
    """
    Abstraction of an author in the Git repository.
    """

    def __init__(self, repo: Repo, name: str, email: str):
        """
        Instantiate an Author.

        Args:
            repo: reference to the global Repo instance
            name: author's full name
            email: author's email
        """
        super().__init__(repo)
        self._name = name
        self._email = email
        self._pages = {}

    def add_lines(self, page: Page, commit: Commit, lines: int = 1):
        """
        Add line(s) in a given page/commit to the author's data.

        Args:
            page: Page object referencing the markdown file
            commit: commit in which the line was edited (=> timestamp)
            lines: number of lines to add. Default: 1
        """
        path = page.path()
        entry = self.page(path, page)
        entry['lines'] += lines
        current_dt = entry.get('datetime')
        commit_dt = commit.datetime()
        if not current_dt or commit_dt > current_dt:
            entry['datetime'] = commit_dt
            entry['datetime_str'] = commit.datetime(str)

    def contribution(self, path=None, _type=float):
        """
        The author's relative contribution to a page or the repository.

        The result is a number between 0 and 1, optionally formatted to percent

        Args:
            path: path to a file or None (default)
                if a path is given the author's contribution to *this* page
                is calculated, otherwise to the whole repository.
            _type: 'float' (default) or 'str'
                if _type refers to the str type the result is a formatted
                string, otherwise the raw floating point number.

        Returns:
            formatted string or floating point number
        """
        lines = self.lines(path)
        total_lines = (
            self.page(path)['page'].total_lines()
            if path
            else self.repo().total_lines()
        )
        result = lines / total_lines
        if _type == float:
            return result
        else:
            return str(round(result * 100, 2)) + '%'

    def datetime(self, path, fmt=str):
        """
        The author's last modification date for a given page.

        Args:
            path: path (str or Path) to a page
            fmt: str (default) or anything

        Returns:
            a formatted string (fmt=str)
            or a datetime.datetime object with tzinfo
        """
        if type(path) == str:
            path = Path(path)
        key = 'datetime_str' if fmt == str else 'datetime'
        return self.page(path).get(key)

    def email(self):
        """
        The author's email address

        Args:

        Returns:
            email address as string
        """
        return self._email

    def lines(self, path=None):
        """
        The author's total number of lines on a page or in the repository.

        Args:
            path: path (str or Page) to a markdown file, or None (default)

        Returns:
            number of lines (int) in the repository (path=None)
            or on the given page.
        """
        if path:
            return self.page(path)['lines']
        else:
            return sum([
                v['lines'] for v in self._pages.values()
            ])

    def name(self):
        """
        The author's full name

        Args:

        Returns:
            The full name as a string.
        """
        return self._name

    def page(self, path, page=None):
        """
        A dictionary with the author's contribution to a page.

        If there is no entry for the given page yet a new one is
        created, optionally using a passed Page object as a fallback
        or creating a new one.

        Args:
            path: path (str or Path) to a page's markdown file
            page: page to use if not already present (default: None)

        Returns:
            dict, indexed by path:
            - page: reference to a (new) Page object
            - lines: author's number of lines in the page
            [
            - datetime
            - datetime_str
            ]: information about the latest modification of the page
            by the author. Will not be present in the freshly instantiated
            entry.
        """
        if type(path) == str:
            path = Path(path)
        if not self._pages.get(path):
            self._pages[path] = {
                'page': page or self.repo().page(path),
                'lines': 0
                # datetime and datetime_str will be populated later
            }
        return self._pages[path]
