from mkdocs_git_authors_plugin import util
import os
from git import Actor, Repo

def test_retrieve_authors(tmp_path):
    
    r = Repo.init(tmp_path)
    
    # Create empty file
    file_name = os.path.join(tmp_path, 'new-file')
    with open(file_name, 'w') as the_file:
        the_file.write('Hello\n')
    
    # Commit
    r.index.add([file_name])
    author = Actor('Tim', 'abc@abc.com')
    r.index.commit("initial commit", author = author)
    
    instance = util.Util(tmp_path)
    authors = instance.get_authors(path = file_name)
    authors[0]['last_datetime'] = None
     
    assert authors == [{
                    'name' : "Tim",
                    'email' : "abc@abc.com",
                    'last_datetime' : None,
                    'lines' : 1,
                    'contribution' : '100.0%'
                }]

def test_summarize_authors():
    
    authors = [
        {'name' : 'Tim',
         'email' : 'abc@abc.com'
        }
    ]
    
    summary = util.Util().summarize(authors)
    assert summary == "<span class='git-authors'><a href='mailto:abc@abc.com'>Tim</a></span>"