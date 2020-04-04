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

import re
import shutil
import os
from click.testing import CliRunner
from mkdocs.__main__ import build_command
import git as gitpython


def build_docs_setup(mkdocs_path, output_path):
    runner = CliRunner()
    return runner.invoke(
        build_command, ["--config-file", mkdocs_path, "--site-dir", str(output_path)]
    )


def test_basic_working(tmp_path):

    result = build_docs_setup("tests/basic_setup/mkdocs.yml", tmp_path)
    assert result.exit_code == 0, (
        "'mkdocs build' command failed. Error: %s" % result.stdout
    )

    index_file = tmp_path / "index.html"
    assert index_file.exists(), "%s does not exist" % index_file

    contents = index_file.read_text()
    assert re.search("<span class='git-page-authors", contents)


def test_project_with_no_commits(tmp_path):
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

    cwd = os.getcwd()
    os.chdir(str(testproject_path))

    # run 'git init'
    gitpython.Repo.init(testproject_path, bare=False)

    result = build_docs_setup(
        str(testproject_path / "website/mkdocs.yml"), str(testproject_path / "site")
    )
    assert result.exit_code == 0, (
        "'mkdocs build' command failed. Error: %s" % result.stdout
    )

    os.chdir(cwd)


def test_building_empty_site(tmp_path):
    """
    Structure:
    
    tmp_path/testproject
    website/
        ├── docs/
        └── mkdocs.yml"""
    testproject_path = tmp_path / "testproject"

    shutil.copytree(
        "tests/basic_setup/empty_site", str(testproject_path / "website" / "docs")
    )
    shutil.copyfile(
        "tests/basic_setup/mkdocs_w_contribution.yml",
        str(testproject_path / "website" / "mkdocs.yml"),
    )

    cwd = os.getcwd()
    os.chdir(str(testproject_path))

    # run 'git init'
    gitpython.Repo.init(testproject_path, bare=False)

    result = build_docs_setup(
        str(testproject_path / "website/mkdocs.yml"), str(testproject_path / "site")
    )
    assert result.exit_code == 0, (
        "'mkdocs build' command failed. Error: %s" % result.stdout
    )

    os.chdir(cwd)
