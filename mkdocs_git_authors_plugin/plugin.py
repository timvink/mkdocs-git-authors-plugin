import re
from mkdocs.plugins import BasePlugin
from .repo import Repo

class GitAuthorsPlugin(BasePlugin):
    def __init__(self):
        self._repo = Repo()

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

        page_obj = self.repo().page(page.file.abs_src_path)

        return re.sub(
            pattern,
            page_obj.authors_summary(),
            markdown,
            flags=re.IGNORECASE
        )

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

        path = page.file.abs_src_path
        page_obj = self.repo().page(path)
        authors = page_obj.authors()

        # NOTE: last_datetime is currently given as a
        # string in the format
        # '2020-02-24 17:49:14 +0100'
        # omitting the 'str' argument would result in a
        # datetime.datetime object with tzinfo instead.
        # Should this be formatted differently?
        context['git_authors'] = [
            {
                'name' : author.name(),
                'email' : author.email(),
                'last_datetime' : author.datetime(path, str),
                'lines' : author.lines(path),
                'contribution' : author.contribution(path, str)
            }
            for author in authors
        ]
        context['git_authors_summary'] = page_obj.authors_summary()

        return context

    def repo(self):
        """
        Reference to the Repo object of the current project.
        """
        return self._repo
