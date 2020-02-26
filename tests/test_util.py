from mkdocs_git_authors_plugin import util
import os
from git import Actor, Repo

def test_empty_file(tmp_path):

    # Create empty file
    file_name = os.path.join(tmp_path, 'new-file')
    open(file_name, 'a').close()

    # Get authors of empty, uncommitted file
    r = Repo.init(tmp_path)
    instance = util.Util(tmp_path)
    authors = instance.get_authors(path = file_name)
    assert authors == []

    # Get authors of empty, committed file
    r.index.add([file_name])
    author = Actor('Tim', 'abc@abc.com')
    r.index.commit("initial commit", author = author)
    authors = instance.get_authors(path = file_name)
    assert authors == []

def test_retrieve_authors(tmp_path):
    """
    Builds a fake git project with some commits.

    pytest offers a `tmp_path`. You can reproduce locally with
    >>> import tempfile
    >>> from pathlib import Path
    >>> tmp_path = Path(tempfile.gettempdir()) / 'pytest-retrieve-authors'
    >>> os.mkdir(tmp_path)

    Args:
        tmp_path (PosixPath): Directory of a tempdir
    """

    # Create file
    file_name = os.path.join(tmp_path, 'new-file')
    with open(file_name, 'w') as the_file:
        the_file.write('Hello\n')

    # Create git repo and commit file
    r = Repo.init(tmp_path)
    r.index.add([file_name])
    author = Actor('Tim', 'abc@abc.com')
    r.index.commit("initial commit", author = author)

    instance = util.Util(tmp_path)
    authors = instance.get_authors(path = file_name)
    # We don't want to test datetime
    authors[0]['last_datetime'] = None

    assert authors == [{
                    'name' : "Tim",
                    'email' : "abc@abc.com",
                    'last_datetime' : None,
                    'lines' : 1,
                    'contribution' : '100.0%'
                }]

    # Now add a line to the file
    # From a second author with same email
    with open(file_name, 'a+') as the_file:
        the_file.write('World\n')
    r.index.add([file_name])
    author = Actor('Tim2', 'abc@abc.com')
    r.index.commit("another commit", author = author)

    instance = util.Util(tmp_path)
    authors = instance.get_authors(path = file_name)
    authors[0]['last_datetime'] = None

    assert authors == [{
                    'name' : "Tim",
                    'email' : "abc@abc.com",
                    'last_datetime' : None,
                    'lines' : 2,
                    'contribution' : '100.0%'
                }]

    # Then a third commit from a new author
    with open(file_name, 'a+') as the_file:
        the_file.write('A new line\n')
    r.index.add([file_name])
    author = Actor('John', 'john@abc.com')
    r.index.commit("third commit", author = author)

    instance = util.Util(tmp_path)
    authors = instance.get_authors(path = file_name)
    authors[0]['last_datetime'] = None
    authors[1]['last_datetime'] = None

    assert authors == [{
                    'name' : "John",
                    'email' : "john@abc.com",
                    'last_datetime' : None,
                    'lines' : 1,
                    'contribution' : '33.33%'
                },{
                    'name' : "Tim",
                    'email' : "abc@abc.com",
                    'last_datetime' : None,
                    'lines' : 2,
                    'contribution' : '66.67%'
                }]

def test_summarize_authors():

    authors = [
        {'name' : 'Tim',
         'email' : 'abc@abc.com',
         'contribution' : '64.23%'
        }
    ]

    config = { 'show_contribution' : False }
    summary = util.Util().summarize(authors, config)
    assert summary == "<span class='git-authors'><a href='mailto:abc@abc.com'>Tim</a></span>"

    config = { 'show_contribution' : True }
    summary = util.Util().summarize(authors, config)
    assert summary == "<span class='git-authors'><a href='mailto:abc@abc.com'>Tim</a> (64.23%)</span>"
