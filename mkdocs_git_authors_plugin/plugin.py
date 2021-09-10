from mkdocs_git_authors_plugin.git.command import GitCommandError
import re
import logging
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

from . import util
from .git.repo import Repo
from mkdocs_git_authors_plugin.ci import raise_ci_warnings
from mkdocs_git_authors_plugin.exclude import exclude

logger = logging.getLogger("mkdocs.plugins")

class GitAuthorsPlugin(BasePlugin):
    config_scheme = (
        ("show_contribution", config_options.Type(bool, default=False)),
        ("show_line_count", config_options.Type(bool, default=False)),
        ("count_empty_lines", config_options.Type(bool, default=True)),
        ("fallback_to_empty", config_options.Type(bool, default=False)),
        ("exclude", config_options.Type(list, default=[])),
        # ('sort_authors_by_name', config_options.Type(bool, default=True)),
        # ('sort_reverse', config_options.Type(bool, default=False))
    )

    def __init__(self):
        self._repo = None
        self._fallback = False

    def on_config(self, config, **kwargs):
        """
        Store the plugin configuration in the Repo object.

        The config event is the first event called on build and is run
        immediately after the user configuration is loaded and validated. Any
        alterations to the config should be made here.

        https://www.mkdocs.org/user-guide/plugins/#on_config

        NOTE: This is only the dictionary with the plugin configuration,
        not the global config which is passed to the various event handlers.

        Args:
            config: global configuration object

        Returns:
            (updated) configuration object
        """
        try:
            self._repo = Repo()
            self._fallback = False
            self.repo().set_config(self.config)
            raise_ci_warnings(path = self.repo()._root)
        except GitCommandError:
            if self.config["fallback_to_empty"]:
                self._fallback = True
                logger.warning(
                    "[git-authors-plugin] Unable to find a git directory and/or git is not installed."
                    " Option 'fallback_to_empty' set to 'true': Falling back to empty authors list"
                )
            else:
                raise

    def on_files(self, files, config, **kwargs):
        """
        Preprocess all markdown pages in the project.

        The files event is called after the files collection is populated from
        the docs_dir. Use this event to add, remove, or alter files in the
        collection. Note that Page objects have not yet been associated with the
        file objects in the collection. Use Page Events to manipulate page
        specific data.

        https://www.mkdocs.org/user-guide/plugins/#on_files

        This populates all the lines and total_lines properties
        of the pages and the repository. The event is executed after on_config,
        but before all other events. When any page or template event
        is called, all pages have already been parsed and their statistics
        been aggregated.
        So in any on_page_XXX event the contributions of an author
        to the current page *and* the repository as a whole are available.

        Args:
            files: global files collection
            config: global configuration object

        Returns:
            global files collection
        """
        if self._fallback:
            return
        for file in files:
            path = file.abs_src_path
            if path.endswith(".md"):
                _ = self.repo().page(path)

    def on_page_content(self, html, page, config, files, **kwargs):
        """
        Replace jinja tag {{ git_site_authors }} in HTML.

        The page_content event is called after the Markdown text is
        rendered to HTML (but before being passed to a template) and
        can be used to alter the HTML body of the page.

        https://www.mkdocs.org/user-guide/plugins/#on_page_content

        We replace the authors list in this event in order to be able
        to replace it with arbitrary HTML content (which might otherwise
        end up in styled HTML in a code block).

        Args:
            html: the processed HTML of the page
            page: mkdocs.nav.Page instance
            config: global configuration object
            site_navigation: global navigation object

        Returns:
            str: HTML text of page as string
        """
        # Exclude pages specified in config
        excluded_pages = self.config.get("exclude", [])
        if exclude(page.file.src_path, excluded_pages):
            logging.debug("on_page_html, Excluding page " + page.file.src_path)
            return html

        list_pattern = re.compile(
            r"\{\{\s*git_site_authors\s*\}\}", flags=re.IGNORECASE
        )
        if list_pattern.search(html):
            html = list_pattern.sub(
                "" if self._fallback else
                util.site_authors_summary(self.repo().get_authors(), self.config), html
            )
        return html

    def on_page_markdown(self, markdown, page, config, files, **kwargs):
        """
        Replace jinja tags in markdown.

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

        # Exclude pages specified in config
        excluded_pages = self.config.get("exclude", [])
        if exclude(page.file.src_path, excluded_pages):
            logging.debug("on_page_markdown, Excluding page " + page.file.src_path)
            return markdown

        pattern_authors_summary = re.compile(
            r"\{\{\s*git_authors_summary\s*\}\}", flags=re.IGNORECASE
        )
        pattern_page_authors = re.compile(
            r"\{\{\s*git_page_authors\s*\}\}", flags=re.IGNORECASE
        )

        if not pattern_authors_summary.search(
            markdown
        ) and not pattern_page_authors.search(markdown):
            return markdown

        if self._fallback:
            markdown = pattern_authors_summary.sub("", markdown)
            markdown = pattern_page_authors.sub("", markdown)
            return markdown

        page_obj = self.repo().page(page.file.abs_src_path)
        page_authors = util.page_authors_summary(page_obj, self.config)

        markdown = pattern_authors_summary.sub(page_authors, markdown)
        markdown = pattern_page_authors.sub(page_authors, markdown)
        return markdown

    def on_page_context(self, context, page, config, nav, **kwargs):
        """
        Add 'git_authors' and 'git_authors_summary' variables
        to template context.

        The page_context event is called after the context for a page
        is created and can be used to alter the context for that
        specific page only.

        https://www.mkdocs.org/user-guide/plugins/#on_page_context

        Note this is called *after* on_page_markdown()

        Args:
            context (dict): template context variables
            page (class): mkdocs.nav.Page instance
            config: global configuration object
            nav: global navigation object

        Returns:
            dict: template context variables
        """
        if self._fallback:
            return context

        # Exclude pages specified in config
        excluded_pages = self.config.get("exclude", [])
        if exclude(page.file.src_path, excluded_pages):
            logging.debug("on_page_context, Excluding page " + page.file.src_path)
            return context

        path = page.file.abs_src_path
        page_obj = self.repo().page(path)
        authors = page_obj.get_authors()

        page_authors = util.page_authors_summary(page_obj, self.config)
        site_authors = util.site_authors_summary(self.repo().get_authors(), self.config)

        # NOTE: last_datetime is currently given as a
        # string in the format
        # '2020-02-24 17:49:14 +0100'
        # omitting the 'str' argument would result in a
        # datetime.datetime object with tzinfo instead.
        # Should this be formatted differently?
        context["git_info"] = {
            "page_authors": util.page_authors(authors, path),
            "site_authors": util.page_authors(self.repo().get_authors(), path),
        }

        # Make available the same markdown tags in jinja context
        context["git_page_authors"] = page_authors
        context["git_site_authors"] = site_authors

        # For backward compatibility, deprecate in 1.2
        context["git_authors"] = util.page_authors(authors, path)
        context["git_authors_summary"] = page_authors

        return context

    def repo(self):
        """
        Reference to the Repo object of the current project.
        """
        return self._repo
