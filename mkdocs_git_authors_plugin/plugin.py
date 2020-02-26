import re
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from .util import Util

class GitAuthorsPlugin(BasePlugin):
    config_scheme = (
        ('show_contribution', config_options.Type(bool, default=False)),
    )

    def __init__(self):
        self.util = Util()

    def on_page_markdown(self, markdown, page, config, files):
        """
        Replace jinja tag {{ git_authors_summary }} in markdown.

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

        pattern = r"\{\{\s*git_authors_summary\s*\}\}"

        if not re.search(pattern, markdown, flags=re.IGNORECASE):
           return markdown

        authors = self.util.get_authors(
            path = page.file.abs_src_path
        )
        authors_summary = self.util.summarize(authors, self.config)

        return re.sub(pattern,
                      authors_summary,
                      markdown,
                      flags=re.IGNORECASE)

    def on_page_context(self, context, page, **kwargs):
        """
        Add 'git_authors' and 'git_authors_summary' variables
        to template context.

        The page_context event is called after the context for a page
        is created and can be used to alter the context for that
        specific page only.

        Note this is called *after* on_page_markdown()

        Args:
            context (dict): template context variables
            page (class): mkdocs.nav.Page instance

        Returns:
            dict: template context variables
        """


        authors = self.util.get_authors(
            path = page.file.abs_src_path
        )
        authors_summary = self.util.summarize(authors, self.config)

        context['git_authors'] = authors
        context['git_authors_summary'] = authors_summary

        return context