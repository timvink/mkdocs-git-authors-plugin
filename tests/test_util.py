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

import logging
import os
import shutil
from typing import Any

# GitPython
import git as gitpython

from mkdocs_git_authors_plugin import util
from mkdocs_git_authors_plugin.git import repo

DEFAULT_CONFIG = {
    "show_contribution": False,
    "show_line_count": False,
    "show_email_address": True,
    "count_empty_lines": True,
    "sort_authors_by_name": True,
    "sort_reverse": False,
    "sort_authors_by": "name",
    "authorship_threshold_percent": 0,
    "ignore_authors": [],
}

#### Helpers ####


def setup_clean_mkdocs_folder(mkdocs_yml_path, output_path) -> Any:
    """
    Sets up a clean mkdocs directory

    outputpath/testproject
    ├── docs/
    └── mkdocs.yml

    Args:
        mkdocs_yml_path (Path): Path of mkdocs.yml file to use
        output_path (Path): Path of folder in which to create mkdocs project

    Returns:
        testproject_path (Path): Path to test project
    """

    testproject_path = output_path / "testproject"

    # Create empty 'testproject' folder
    if os.path.exists(testproject_path):
        logging.warning(
            """This command does not work on windows. 
        Refactor your test to use setup_clean_mkdocs_folder() only once"""
        )
        shutil.rmtree(testproject_path)

    # Copy correct mkdocs.yml file and our test 'docs/'
    shutil.copytree("tests/basic_setup/docs", testproject_path / "docs")
    shutil.copyfile(mkdocs_yml_path, testproject_path / "mkdocs.yml")

    return testproject_path


def setup_commit_history(testproject_path):
    """
    Initializes and creates a git commit history
    in a new mkdocs testproject.

    We commit the pages one by one in order
    to create some git depth.

    Args:
        testproject_path (Path): Path to test project

    Returns:
        repo (repo): git.Repo object
    """
    assert not os.path.exists(testproject_path / ".git")

    repo = gitpython.Repo.init(testproject_path, bare=False)
    author = "Test Person <testtest@gmail.com>"

    # Change the working directory
    cwd = os.getcwd()
    os.chdir(str(testproject_path))

    try:
        repo.git.add("mkdocs.yml")
        repo.git.commit(message="add mkdocs", author=author)

        repo.git.add("docs/first_page.md")
        repo.git.commit(message="first page", author=author)
        file_name = testproject_path / "docs/first_page.md"
        with open(file_name, "w+") as the_file:
            the_file.write("Hello\n")
        repo.git.add("docs/first_page.md")
        repo.git.commit(message="first page update 1", author=author)
        with open(file_name, "w") as the_file:
            the_file.write("# First Test Page Edited\n\nSome Lorem text")
        repo.git.add("docs/first_page.md")
        repo.git.commit(message="first page update 2", author=author)

        repo.git.add("docs/second_page.md")
        repo.git.commit(message="second page", author=author)
        repo.git.add("docs/index.md")
        repo.git.commit(message="homepage", author=author)
        repo.git.add("docs/page_with_tag.md")
        repo.git.commit(message="homepage", author=author)
        os.chdir(str(cwd))
    except:
        os.chdir(str(cwd))
        raise

    os.chdir(cwd)
    return repo


#### Tests ####


def test_empty_file(tmp_path) -> None:
    # Change working directory
    cwd = os.getcwd()
    os.chdir(str(tmp_path))

    # Create empty file
    file_name = str(tmp_path / "new-file")
    open(file_name, "a").close()

    # Get authors of empty, uncommitted file
    r = gitpython.Repo.init(tmp_path)

    repo_instance = repo.Repo()
    repo_instance.set_config(DEFAULT_CONFIG)
    # TODO: should throw an error?
    repo_instance.page(file_name)

    authors = repo_instance.get_authors()
    assert authors == []

    # Get authors of empty but committed file
    r.index.add([file_name])
    author = gitpython.Actor("Tim", "abc@abc.com")
    r.index.commit("initial commit", author=author)

    repo_instance.page(file_name)
    authors = repo_instance.get_authors()
    assert authors == []

    os.chdir(cwd)
    ## TODO
    # When the first instance of a commit on a page is skipped as an empty line,
    # the second instance will not have the commit metadata available


def test_retrieve_authors(tmp_path):
    """
    Builds a fake git project with some commits.

    Args:
        tmp_path (PosixPath): Directory of a tempdir
    """
    cwd = os.getcwd()
    os.chdir(str(tmp_path))

    # Create file
    file_name = str(tmp_path / "new-file")
    with open(file_name, "w") as the_file:
        the_file.write("Hello\n")

    # Create git repo and commit file
    r = gitpython.Repo.init(tmp_path)
    r.index.add([file_name])
    author = gitpython.Actor("Tim", "abc@abc.com")
    r.index.commit("initial commit", author=author)

    # Test retrieving author
    repo_instance = repo.Repo()
    repo_instance.set_config(DEFAULT_CONFIG)
    repo_instance.page(file_name)

    authors = repo_instance.get_authors()
    assert len(authors) == 1
    # We don't want to test datetime
    authors = util.page_authors(authors, file_name)
    authors[0]["last_datetime"] = None

    assert authors == [
        {
            "name": "Tim",
            "email": "abc@abc.com",
            "last_datetime": None,
            "lines": 1,
            "lines_all_pages": 1,
            "contribution": "100.0%",
            "contribution_all_pages": "100.0%",
        }
    ]

    # Now add a line to the file
    # From a second author with same email
    with open(file_name, "a+") as the_file:
        the_file.write("World\n")
    r.index.add([file_name])
    author = gitpython.Actor("Tim2", "abc@abc.com")
    r.index.commit("another commit", author=author)

    repo_instance = repo.Repo()
    repo_instance.set_config(DEFAULT_CONFIG)
    repo_instance.page(file_name)
    authors = repo_instance.get_authors()
    authors = util.page_authors(authors, file_name)
    authors[0]["last_datetime"] = None

    assert authors == [
        {
            "name": "Tim",
            "email": "abc@abc.com",
            "last_datetime": None,
            "lines": 2,
            "lines_all_pages": 2,
            "contribution": "100.0%",
            "contribution_all_pages": "100.0%",
        }
    ]

    # Then a third commit from a new author
    with open(file_name, "a+") as the_file:
        the_file.write("A new line\n")
    r.index.add([file_name])
    author = gitpython.Actor("John", "john@abc.com")
    r.index.commit("third commit", author=author)

    repo_instance = repo.Repo()
    repo_instance.set_config(DEFAULT_CONFIG)
    repo_instance.page(file_name)
    authors = repo_instance.get_authors()
    authors = util.page_authors(authors, file_name)
    authors[0]["last_datetime"] = None
    authors[1]["last_datetime"] = None

    assert authors == [
        {
            "name": "John",
            "email": "john@abc.com",
            "last_datetime": None,
            "lines": 1,
            "lines_all_pages": 1,
            "contribution": "33.33%",
            "contribution_all_pages": "33.33%",
        },
        {
            "name": "Tim",
            "email": "abc@abc.com",
            "last_datetime": None,
            "lines": 2,
            "lines_all_pages": 2,
            "contribution": "66.67%",
            "contribution_all_pages": "66.67%",
        },
    ]
    os.chdir(cwd)


def test_retrieve_authors_ignoring_commits(tmp_path):
    """
    Builds a fake git project with some commits.

    Args:
        tmp_path (PosixPath): Directory of a tempdir
    """
    cwd = os.getcwd()
    os.chdir(str(tmp_path))

    # Create file
    file_name = str(tmp_path / "new-file")
    with open(file_name, "w") as the_file:
        the_file.write("line 1\n")
        the_file.write("line 2\n")

    # Create git repo and commit file
    r = gitpython.Repo.init(tmp_path)
    r.index.add([file_name])
    author = gitpython.Actor("Tim", "abc@abc.com")
    r.index.commit("initial commit", author=author)

    # Update the file
    with open(file_name, "w") as the_file:
        the_file.write("line 1.1\n")
        the_file.write("line 2.1\n")
    r.index.add([file_name])
    author = gitpython.Actor("John", "john@abc.com")
    commit = r.index.commit("second commit", author=author)

    repo_instance = repo.Repo()
    repo_instance.set_config(DEFAULT_CONFIG)
    repo_instance.page(file_name)
    authors = repo_instance.get_authors()
    authors = util.page_authors(authors, file_name)
    authors[0]["last_datetime"] = None

    assert authors == [
        {
            "name": "John",
            "email": "john@abc.com",
            "last_datetime": None,
            "lines": 2,
            "lines_all_pages": 2,
            "contribution": "100.0%",
            "contribution_all_pages": "100.0%",
        }
    ]

    # Get the authors while ignoring the last commit
    ignored_commits_files = str(tmp_path / "ignored_commits.txt")
    with open(ignored_commits_files, "w") as the_file:
        the_file.write(commit.hexsha + "\n")
    repo_instance = repo.Repo()
    config = DEFAULT_CONFIG.copy()
    config["ignore_commits"] = ignored_commits_files
    repo_instance.set_config(config)
    repo_instance.page(file_name)
    authors = repo_instance.get_authors()
    authors = util.page_authors(authors, file_name)
    authors[0]["last_datetime"] = None

    assert authors == [
        {
            "name": "Tim",
            "email": "abc@abc.com",
            "last_datetime": None,
            "lines": 2,
            "lines_all_pages": 2,
            "contribution": "100.0%",
            "contribution_all_pages": "100.0%",
        },
    ]

    os.chdir(cwd)


def test_retrieve_authors_ignoring_emails(tmp_path):
    """
    Builds a fake git project with some commits.

    Args:
        tmp_path (PosixPath): Directory of a tempdir
    """
    cwd = os.getcwd()
    os.chdir(str(tmp_path))

    # Create file
    file_name = str(tmp_path / "new-file")
    with open(file_name, "w") as the_file:
        the_file.write("line 1\n")
        the_file.write("line 2\n")

    # Create git repo and commit file
    r = gitpython.Repo.init(tmp_path)
    r.index.add([file_name])
    author = gitpython.Actor("Tim", "abc@abc.com")
    r.index.commit("initial commit", author=author)

    # Add more content
    with open(file_name, "a+") as the_file:
        the_file.write("line 3\n")
        the_file.write("line 4\n")
    r.index.add([file_name])
    author = gitpython.Actor("John", "john@abc.com")
    r.index.commit("second commit", author=author)

    # Get the authors while ignoring john@abc.com user
    repo_instance = repo.Repo()
    config = DEFAULT_CONFIG.copy()
    config["ignore_authors"] = ["john@abc.com"]
    repo_instance.set_config(config)
    repo_instance.page(file_name)
    authors = repo_instance.get_authors()
    authors = util.page_authors(authors, file_name)
    authors[0]["last_datetime"] = None
    authors[1]["last_datetime"] = None

    assert authors == [
        {
            "contribution": "0.0%",
            "contribution_all_pages": "0.0%",
            "email": "john@abc.com",
            "last_datetime": None,
            "lines": 0,
            "lines_all_pages": 0,
            "name": "John",
        },
        {
            "name": "Tim",
            "email": "abc@abc.com",
            "last_datetime": None,
            "lines": 2,
            "lines_all_pages": 2,
            "contribution": "100.0%",
            "contribution_all_pages": "100.0%",
        },
    ]

    os.chdir(cwd)


def test_mkdocs_in_git_subdir(tmp_path):
    """
    Sometimes `mkdocs.yml` is not in the root of the repo.
    We need to make sure things still work in this edge case.

    tmp_path/testproject
    website/
        ├── docs/
        └── mkdocs.yml
    """
    testproject_path = tmp_path / "testproject"

    shutil.copytree(
        "tests/basic_setup/docs", str(testproject_path / "website" / "docs")
    )
    shutil.copyfile(
        "tests/basic_setup/mkdocs.yml", str(testproject_path / "website" / "mkdocs.yml")
    )

    cwd = os.getcwd()
    os.chdir(str(testproject_path))

    # Create file
    file_name = str(testproject_path / "website" / "new-file")
    with open(file_name, "w") as the_file:
        the_file.write("Hello\n")

    # Create git repo and commit file
    r = gitpython.Repo.init(testproject_path)
    r.index.add([file_name])
    author = gitpython.Actor("Tim", "abc@abc.com")
    r.index.commit("initial commit", author=author)

    # Test retrieving author
    repo_instance = repo.Repo()
    repo_instance.set_config(DEFAULT_CONFIG)
    repo_instance.page(file_name)

    authors = repo_instance.get_authors()
    assert len(authors) == 1
    # We don't want to test datetime
    authors = util.page_authors(authors, file_name)
    authors[0]["last_datetime"] = None

    assert authors == [
        {
            "name": "Tim",
            "email": "abc@abc.com",
            "last_datetime": None,
            "lines": 1,
            "lines_all_pages": 1,
            "contribution": "100.0%",
            "contribution_all_pages": "100.0%",
        }
    ]

    os.chdir(cwd)


def test_summarize_authors():
    """
    Test summary functions.
    TODO
    """
    pass
    # authors = [
    #     {'name' : 'Tim',
    #      'email' : 'abc@abc.com',
    #      'contribution' : '64.23%'
    #     }
    # ]

    # # Default case: don't show contribution
    # config = { 'show_contribution' : False }
    # summary = util.Util().summarize(authors, config)
    # assert summary == "<span class='git-authors'><a href='mailto:abc@abc.com'>Tim</a></span>"

    # # Do show contribution,
    # # but hide it because there's only one author
    # config = { 'show_contribution' : True }
    # summary = util.Util().summarize(authors, config)
    # assert summary == "<span class='git-authors'><a href='mailto:abc@abc.com'>Tim</a></span>"

    # # Add another author
    # authors.append({
    #     'name' : 'Tom',
    #     'email' : 'efg@efg.org',
    #     'contribution' : '35.77%'
    # })
    # # Now contribution is displayed
    # summary = util.Util().summarize(authors, config)
    # assert summary == "<span class='git-authors'><a href='mailto:abc@abc.com'>Tim</a> (64.23%), <a href='mailto:efg@efg.org'>Tom</a> (35.77%)</span>"


# TODO: test authors threshold with commits
