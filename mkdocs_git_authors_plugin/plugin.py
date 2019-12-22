import re
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from mkdocs.utils import string_types
from .util import Util

class GitAuthorsPlugin(BasePlugin):
    config_scheme = (
        ('type', config_options.Type(string_types, default='')),
    )

    def __init__(self):
        self.util = Util()
   
    def on_page_markdown(self, markdown, page, config, files):
        """
        Replace jinja2 tags in markdown and templates.
        
        The page_markdown event is called after the page's markdown is loaded 
        from file and can be used to alter the Markdown source text. 
        The meta- data has been stripped off and is available as page.meta 
        at this point.
        
        https://www.mkdocs.org/user-guide/plugins/#on_page_markdown
        
        Args:
            markdown (str): Markdown source text of page as string
            page: mkdocs.nav.Page instance
            config: global configuration object
            site_navigation: global navigation object
            
        Returns:
            str: Markdown source text of page as string
        """

        authors = self.util.get_authors(
            path = page.file.abs_src_path,
            type = self.config['type']
        )
        
        return re.sub(r"\{\{\s*git_authors\s*\}\}",
                        authors,
                        markdown,
                        flags=re.IGNORECASE)
        
