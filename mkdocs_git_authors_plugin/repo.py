import os
import subprocess

from collections import OrderedDict
from datetime import datetime, timedelta, timezone

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

        - command a string ('git' will implicitly be prepended)
        - args: a string list with remaining command arguments.
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
        """
        self._args = args

    def set_command(self, command: str):
        """
        Change the Git command.
        """
        self._command = command

    def stderr(self):
        """
        Return the stderr output of the command as a string list.
        """
        if not self._completed:
            raise GitCommandError('Trying to read from uncompleted GitCommand')
        return self._stderr

    def stdout(self):
        """
        Return the stdout output of the command as a string list.
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

        # Store Commit, indexed by 40 char SHA
        self._commits = {}
        # Store Page objects, indexed by path
        self._pages = {}

    def blame(self, path: str):
        """
        Return the cached Page object for path.
        """
        if not self._pages.get(path):
            self._pages[path] = Page(self, path)
        return self._pages[path].commits()

    def commit(self, sha: str):
        """
        Return the cached Commit object for sha.
        """
        if not self._commits.get(sha):
            self._commits[sha] = Commit(self, sha)
        return self._commits.get(sha)

    def find_repo_root(self):
        """
        Determine the root directory of the Git repository,
        in case the current working directory is different from that.

        Raises a GitCommandError if we're not in a Git repository
        (or Git is not installed).
        """
        cmd = GitCommand('rev-parse', ['--show-toplevel'])
        cmd.run()
        return cmd.stdout()[0]

    def root(self):
        """
        Returns the repository root.
        """
        return self._root


class AbstractRepoObject(object):
    """
    Base class for objects that live with a repository context.
    """

    def __init__(self, repo: Repo):
        self._repo = repo

    def repo(self):
        """
        Return a reference to the Repo object.
        """
        return self._repo


class Commit(AbstractRepoObject):
    """
    Information about a single commit.

    Stores only information relevant to our plugin:
    - author name and email,
    - date/time
    """

    def __init__(self, repo: Repo, sha: str):
        super().__init__(repo)
        self._sha = sha
        self._populate()

    def author_name(self):
        """
        The commit's author name.
        """
        return self._author_name

    def author_email(self):
        """
        The commit's author email.
        """
        return self._author_email

    def datetime(self):
        """
        The commit's commit time.

        Stored as a datetime.datetime object with timezone information.
        """
        return self._datetime

    def _populate(self):
        """
        Retrieve information about the commit.
        """
        cmd = GitCommand('show', [
            '-t',
            '--quiet',
            "--format='%aN%n%aE%n%ai'",
            self.sha()
        ])
        cmd.run()
        result = cmd.stdout()

        # Author name and email are returned on single lines.
        self._author_name = result[0]
        self._author_email = result[1]
        # Third line includes formatted date/time info
        d, t, tz = result[2].split(' ')
        d = [int(v) for v in d.split('-')]
        t = [int(v) for v in t.split(':')]
        # timezone info looks like +hhmm or -hhmm
        tz_hours = int(tz[:3])
        th_minutes = int(tz[0] + tz[3:])
        tzinfo = timezone(timedelta(hours=tz_hours,minutes=th_minutes))
        # Construct 'aware' datetime.datetime object
        self._datetime = datetime(
            d[0], d[1], d[2], t[0], t[1], t[2], tzinfo=tzinfo
        )

    def sha(self):
        """
        Return the commit's 40 byte SHA.
        """
        return self._sha


class Page(AbstractRepoObject):
    """
    Results of git blame for a given file.

    Stores a list of tuples with a reference to a
    Commit object and a list of consecutive lines
    modified by that commit.
    """

    def __init__(self, repo: Repo, path: str):
        super().__init__(repo)
        self._path = path
        self._commits = []
        self._execute()

    def commits(self):
        """
        Returns the list of blame commits for the given file.

        Each item in this list is a tuple of
        - a Commit object
        - a string list of lines affected by this commit.
        """
        return self._commits

    def _execute(self):
        """
        Execute git blame and parse the results.
        """

        cmd = GitCommand('blame', ['-lts', self._path])
        cmd.run()
        result = cmd.stdout()

        current_sha = ''
        for line in result:
            # split result line
            sha = line[:40]
            # formatted line number, separated by spaces
            offset = line[41:].find(' ')
            content = line[42+offset:]
            if current_sha != sha:
                # line has different commit than previous one
                self._commits.append((
                    self.repo().commit(sha),
                    [content]
                ))
            elif sha:
                # append line to previous commit's lines list
                self._commits[-1][1].append(content)
