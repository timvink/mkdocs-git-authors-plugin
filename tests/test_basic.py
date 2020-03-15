import re
from click.testing import CliRunner
from mkdocs.__main__ import build_command


def build_docs_setup(mkdocs_path, output_path):
    runner = CliRunner()
    return runner.invoke(build_command, 
                ['--config-file', 
                 mkdocs_path, 
                 '--site-dir', 
                 str(output_path)])
    
def test_basic_working(tmp_path):

    result = build_docs_setup('tests/basic_setup/mkdocs.yml', tmp_path)
    assert result.exit_code == 0, "'mkdocs build' command failed"

    index_file = tmp_path/'index.html'
    assert index_file.exists(),  "%s does not exist" % index_file
    
    contents = index_file.read_text()
    assert re.search("<span class='git-authors'>", contents)

    
