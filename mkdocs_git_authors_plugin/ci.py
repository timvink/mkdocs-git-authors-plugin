"""
Helper functions related to continuous integration (CI).

This is because often CI runners do not have access to full git history.

Taken from https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/blob/master/mkdocs_git_revision_date_localized_plugin/ci.py
"""

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Union

from mkdocs_git_authors_plugin.git.command import GitCommand


@contextmanager
def working_directory(path: Union[str, Path]) -> Generator[None, Any, None]:
    """
    Temporarily change working directory.
    A context manager which changes the working directory to the given
    path, and then changes it back to its previous value on exit.
    Usage:
    ```python
    # Do something in original directory
    with working_directory('/my/new/path'):
        # Do something in new directory
    # Back to old directory
    ```
    """
    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


def raise_ci_warnings(path: str) -> None:
    """
    Raise warnings when users use plugin on CI build runners.

    Args:
        path (str): path to the root of the git repo
    """
    with working_directory(path):
        if not is_shallow_clone():
            return None

        n_commits = commit_count()

    # Gitlab Runners
    if os.getenv("GITLAB_CI") is not None and n_commits < 50:
        # Default is GIT_DEPTH of 50 for gitlab
        logging.warning(
            """
                [git-authors] Running on a GitLab runner might lead to wrong
                Git revision dates due to a shallow git fetch depth.

                Make sure to set GIT_DEPTH to 1000 in your .gitlab-ci.yml file
                (see https://docs.gitlab.com/ee/user/project/pipelines/settings.html#git-shallow-clone).
                """
        )

    # Github Actions
    if os.getenv("GITHUB_ACTIONS") is not None and n_commits == 1:
        # Default is fetch-depth of 1 for github actions
        logging.warning(
            """
                [git-authors] Running on GitHub Actions might lead to wrong
                Git revision dates due to a shallow git fetch depth.

                Try setting fetch-depth to 0 in your GitHub Action
                (see https://github.com/actions/checkout).
                """
        )

    # Bitbucket pipelines
    if os.getenv("CI") is not None and n_commits < 50:
        # Default is fetch-depth of 50 for bitbucket pipelines
        logging.warning(
            """
                [git-authors] Running on bitbucket pipelines might lead to wrong
                Git revision dates due to a shallow git fetch depth.

                Try setting "clone: depth" to "full" in your pipeline
                (see https://support.atlassian.com/bitbucket-cloud/docs/configure-bitbucket-pipelinesyml/
                and search 'depth').
                """
        )

    # Azure Devops Pipeline
    # Does not limit fetch-depth by default
    if int(os.getenv("Agent.Source.Git.ShallowFetchDepth", 10e99)) < n_commits:
        logging.warning(
            """
                [git-authors] Running on Azure pipelines with limited
                fetch-depth might lead to wrong git revision dates due to a shallow git fetch depth.

                Remove any Shallow Fetch settings
                (see https://docs.microsoft.com/en-us/azure/devops/pipelines/repos/pipeline-options-for-git?view=azure-devops#shallow-fetch).
                """
        )


def commit_count() -> int:
    """
    Determine the number of commits in a repository.

    Returns:
        count (int): Number of commits.
    """
    gc = GitCommand("rev-list", ["--count", "HEAD"])
    gc.run()
    n_commits = int(gc._stdout[0])  # type: ignore
    assert n_commits >= 0
    return n_commits


def is_shallow_clone() -> bool:
    """
    Determine if repository is a shallow clone.

    References & Context:
    https://github.com/timvink/mkdocs-git-revision-date-localized-plugin/issues/10
    https://stackoverflow.com/a/37203240/5525118

    Returns:
        bool: If a repo is shallow clone
    """
    return os.path.exists(".git/shallow")
