"""
Note that pytest offers a `tmp_path`.
You can reproduce locally with

```python
%load_ext autoreload
%autoreload 2
import os
import tempfile
import shutil
from pathlib import Path
tmp_path = Path(tempfile.gettempdir()) / 'pytest-retrieve-authors'
if os.path.exists(tmp_path):
    shutil.rmtree(tmp_path)
os.mkdir(tmp_path)
```
"""

import os
import re
import shutil
import sys
from contextlib import contextmanager
from packaging.version import Version
from typing import Any, Generator

import git as gitpython
import mkdocs
import pytest
from click.testing import CliRunner, Result
from git import Repo
from mkdocs.__main__ import build_command

SITES_THAT_SHOULD_SUCCEED = [
    "mkdocs.yml",
    "mkdocs_complete_material.yml",
    "mkdocs_exclude.yml",
    "mkdocs_fallback.yml",
    "mkdocs_genfiles.yml",
    "mkdocs_w_contribution_and_author_threshold.yml",
    "mkdocs_w_contribution_sort_and_author_threshold.yml",
    "mkdocs_w_contribution.yml",
    "mkdocs_w_macros.yml",
    "mkdocs_w_macros2.yml",
]


@contextmanager
def working_directory(path) -> Generator[None, Any, None]:
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
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def build_docs_setup(mkdocs_path, output_path) -> Result:
    runner = CliRunner()
    return runner.invoke(
        build_command, ["--config-file", mkdocs_path, "--site-dir", str(output_path)]
    )


@pytest.mark.parametrize(
    "mkdocs_file",
    SITES_THAT_SHOULD_SUCCEED,
)
def test_basic_working(tmp_path, mkdocs_file: str) -> None:
    """
    combination with mkdocs-macros-plugin lead to error.
    See https://github.com/timvink/mkdocs-git-authors-plugin/issues/60
    """
    result = build_docs_setup(f"tests/basic_setup/{mkdocs_file}", tmp_path)
    assert (
        result.exit_code == 0
    ), f"'mkdocs build' command failed. Error: {result.stdout}"

    index_file = tmp_path / "index.html"
    assert index_file.exists(), f"{index_file} does not exist"

    contents = index_file.read_text()
    assert re.search("<span class='git-page-authors", contents)
    assert re.search('<a href="mailto:vinktim@gmail.com">Tim Vink</a>', contents)


def test_custom_href(tmp_path) -> None:
    """ """
    result = build_docs_setup("tests/basic_setup/mkdocs_custom_href.yml", tmp_path)
    assert (
        result.exit_code == 0
    ), f"'mkdocs build' command failed. Error: {result.stdout}"

    index_file = tmp_path / "index.html"
    assert index_file.exists(), f"{index_file} does not exist"

    contents = index_file.read_text()
    assert re.search("<span class='git-page-authors", contents)
    # Checking Page Authors
    assert re.search(
        r"<p>Page authors:.*<a href='https://teams.microsoft.com/l/chat/0/0\?"
        r"users=vinktim@gmail.com'>Tim Vink</a>.*</p>",
        contents,
    )
    # Checking Site Authors
    assert re.search(
        r'<li><a href="https://teams.microsoft.com/l/chat/0/0\?'
        r'users=vinktim@gmail.com">Tim Vink</a></li>',
        contents,
    )


def test_no_email(tmp_path) -> None:
    result = build_docs_setup("tests/basic_setup/mkdocs_no_email.yml", tmp_path)
    assert (
        result.exit_code == 0
    ), f"'mkdocs build' command failed. Error: {result.stdout}"

    index_file = tmp_path / "index.html"
    assert index_file.exists(), f"{index_file} does not exist"

    contents = index_file.read_text()
    assert re.search("<span class='git-page-authors", contents)
    assert re.search("<li>Tim Vink</li>", contents)


def test_exclude_working(tmp_path) -> None:
    result = build_docs_setup("tests/basic_setup/mkdocs_exclude.yml", tmp_path)
    assert (
        result.exit_code == 0
    ), f"'mkdocs build' command failed. Error: {result.stdout}"

    page_file = tmp_path / "page_with_tag/index.html"
    assert page_file.exists(), f"{page_file} does not exist"

    contents = page_file.read_text()
    assert not re.search("<span class='git-page-authors", contents)


def test_ignore_authors_working(tmp_path) -> None:
    result = build_docs_setup("tests/basic_setup/mkdocs_ignore_authors.yml", tmp_path)
    assert (
        result.exit_code == 0
    ), f"'mkdocs build' command failed. Error: {result.stdout}"

    page_file = tmp_path / "page_with_tag/index.html"
    assert page_file.exists(), f"{page_file} does not exist"

    contents = page_file.read_text()
    assert re.search("<span class='git-page-authors", contents)
    assert re.search("<a href='mailto:vinktim@gmail.com'>Tim Vink</a>", contents)
    assert not re.search("Julien", contents)


def test_exclude_working_with_genfiles(tmp_path) -> None:
    """
    A warning for uncommited files should not show up
    when those uncommited files are excluded.
    """

    testproject_path = tmp_path / "testproject_genfiles"

    shutil.copytree("tests/basic_setup/docs", str(testproject_path / "docs"))
    shutil.copyfile(
        "tests/basic_setup/mkdocs_genfiles.yml",
        str(testproject_path / "mkdocs.yml"),
    )

    with working_directory(str(testproject_path)):
        # setup git history
        repo = Repo.init(testproject_path)
        assert not repo.bare
        repo.git.add(all=True)
        repo.index.commit("first commit")

        # generate a file manually, do not commit
        with open(testproject_path / "docs" / "manually_created.md", "w") as f:
            f.write("Hello, world!")

        # generate another file manually, do not commit
        another_path = testproject_path / "docs" / "somefolder"
        os.mkdir(another_path)
        with open(another_path / "manually_created_infolder.md", "w") as f:
            f.write("Hello, world!")

        # mkdocs build
        # mkdocs.yml has exclusions for the created files
        result = build_docs_setup(
            str(testproject_path / "mkdocs.yml"), str(testproject_path / "site")
        )
        assert (
            result.exit_code == 0
        ), f"'mkdocs build' command failed. Error: { result.stdout}"

        # files generated ourselves right before build but not committed, should not generate warnings
        assert "manually_created.md has not been committed yet." not in result.stdout
        assert (
            "manually_created_infolder.md has not been committed yet."
            not in result.stdout
        )


def test_enabled_working(tmp_path) -> None:
    result = build_docs_setup(
        "tests/basic_setup/mkdocs_complete_material_disabled.yml", tmp_path
    )
    assert (
        result.exit_code == 0
    ), f"'mkdocs build' command failed. Error: {result.stdout}"

    page_file = tmp_path / "page_with_tag/index.html"
    assert page_file.exists(), f"{page_file} does not exist"

    contents = page_file.read_text()
    assert not re.search("<span class='git-page-authors", contents)


def test_project_with_no_commits(tmp_path) -> None:
    """
    Structure:

    tmp_path/testproject
    website/
        ├── docs/
        └── mkdocs.yml"""
    testproject_path = tmp_path / "testproject"

    shutil.copytree(
        "tests/basic_setup/docs", str(testproject_path / "website" / "docs")
    )
    shutil.copyfile(
        "tests/basic_setup/mkdocs_w_contribution.yml",
        str(testproject_path / "website" / "mkdocs.yml"),
    )

    with working_directory(str(testproject_path)):
        # run 'git init'
        gitpython.Repo.init(testproject_path, bare=False)

        result = build_docs_setup(
            str(testproject_path / "website/mkdocs.yml"), str(testproject_path / "site")
        )
        assert (
            result.exit_code == 0
        ), f"'mkdocs build' command failed. Error: {result.stdout}"


def test_building_empty_site(tmp_path) -> None:
    """
    Structure:

    ```
    tmp_path/testproject
    website/
        ├── docs/
        └── mkdocs.yml
    ````
    """
    testproject_path = tmp_path / "testproject"

    shutil.copytree(
        "tests/basic_setup/empty_site", str(testproject_path / "website" / "docs")
    )
    shutil.copyfile(
        "tests/basic_setup/mkdocs_w_contribution.yml",
        str(testproject_path / "website" / "mkdocs.yml"),
    )

    with working_directory(str(testproject_path)):
        # run 'git init'
        gitpython.Repo.init(testproject_path, bare=False)

        result = build_docs_setup(
            str(testproject_path / "website/mkdocs.yml"), str(testproject_path / "site")
        )
        assert (
            result.exit_code == 0
        ), f"'mkdocs build' command failed. Error: {result.stdout}"


def test_fallback(tmp_path) -> None:
    """
    Structure:

    ```
    tmp_path/testproject
    website/
        ├── docs/
        └── mkdocs.yml
    ````
    """
    testproject_path = tmp_path / "testproject"

    shutil.copytree(
        "tests/basic_setup/docs", str(testproject_path / "website" / "docs")
    )
    shutil.copyfile(
        "tests/basic_setup/mkdocs_fallback.yml",
        str(testproject_path / "website" / "mkdocs.yml"),
    )

    with working_directory(str(testproject_path)):
        result = build_docs_setup(
            str(testproject_path / "website/mkdocs.yml"), str(testproject_path / "site")
        )
        # import pdb; pdb.set_trace()
        assert (
            result.exit_code == 0
        ), f"'mkdocs build' command failed. Error: {result.stdout}"


# https://github.com/daizutabi/mkapi#:~:text=Python%203.10%20or,1.6%20or%20higher
@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10 or higher")
@pytest.mark.skipif(
    Version(mkdocs.__version__) < Version("1.6"),
    reason="Requires mkdocs 1.6 or higher",
)
def test_mkapi_v3(tmp_path) -> None:
    """Test mkapi v2.1.0 and higher, basically only v3"""
    result = build_docs_setup("tests/basic_setup/mkdocs_mkapi.yml", tmp_path)
    assert (
        result.exit_code == 0
    ), f"'mkdocs build' command failed. Error: {result.stdout}"

    index_file = tmp_path / "index.html"
    assert index_file.exists(), f"{index_file} does not exist"

    contents = index_file.read_text()
    assert re.search("<span class='git-page-authors", contents)
    assert re.search(
        '<a href="#" class="nav-link dropdown-toggle" role="button" data-bs-toggle="dropdown"  aria-expanded="false">API</a>',
        contents,
    )


@pytest.mark.skipif(sys.version_info < (3, 12), reason="Requires Python 3.12 or higher")
@pytest.mark.skip("mkapi v2.0.X requires a currently unsupported Python version")
def test_mkapi_v20x(tmp_path) -> None:
    assert True


@pytest.mark.skipif(sys.version_info < (3, 7) or sys.version_info > (3, 9), reason="Requires Python 3.7 or higher")
@pytest.mark.skipif(
    not (
        Version(mkdocs.__version__) < Version("1.6")
    ),
    reason="Requires mkdocs  >= 1.6",
)
def test_mkapi_v1(tmp_path) -> None:
    result = build_docs_setup("tests/basic_setup/mkdocs_mkapi.yml", tmp_path)
    assert (
        result.exit_code == 0
    ), f"'mkdocs build' command failed. Error: {result.stdout}"

    index_file = tmp_path / "index.html"
    assert index_file.exists(), f"{index_file} does not exist"

    contents = index_file.read_text()
    assert re.search("<span class='git-page-authors", contents)
    assert re.search(
        r'<a href="\$api:src/mkdocs_git_authors_plugin.*" class="nav-link">API</a>',
        contents,
    )
