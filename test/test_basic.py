import re
import yaml
from click.testing import CliRunner
from mkdocs.__main__ import build_command


def load_config(mkdocs_path):
    return yaml.load(open(mkdocs_path, 'rb'), Loader=yaml.Loader)
    
def build_docs_setup(mkdocs_path, output_path):
    runner = CliRunner()
    return runner.invoke(build_command, 
                ['--config-file', 
                 mkdocs_path, 
                 '--site-dir', 
                 str(output_path)])
    
def test_basic_working(tmp_path):

    result = build_docs_setup('test/basic_setup/mkdocs.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    index_file = tmp_path/'index.html'
    assert index_file.exists(),  f"{index_file} does not exist"
    
    contents = index_file.read_text()
    assert re.search("<span class='git-authors'>", contents)