import logging
import re
from typing import Literal, Union

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page
from mkdocs.utils.templates import TemplateContext

from mkdocs_git_authors_plugin import util
from mkdocs_git_authors_plugin.ci import raise_ci_warnings
from mkdocs_git_authors_plugin.config import GitAuthorsPluginConfig
from mkdocs_git_authors_plugin.exclude import exclude
from mkdocs_git_authors_plugin.git.command import GitCommandError
from mkdocs_git_authors_plugin.git.repo import Repo

logger = logging.getLogger("mkdocs.plugins")


class GitAuthorsPlugin(BasePlugin[GitAuthorsPluginConfig]):
    def __init__(self) -> None:
        self._repo = None
        self._fallback = False
        self.is_serve = False

    def on_startup(
        self, command: Literal["build", "gh-deploy", "serve"], dirty: bool
    ) -> None:
        self.is_serve = command == "serve"

    def on_config(self, config: MkDocsConfig) -> Union[MkDocsConfig, None]:
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

        if not self._is_enabled():
            return config

        assert self.config.authorship_threshold_percent >= 0
        assert self.config.authorship_threshold_percent <= 100

        try:
            self._repo = Repo()
            self._fallback = False
            self.repo().set_config(self.config)
            raise_ci_warnings(path=self.repo()._root)
        except GitCommandError:
            if self.config.fallback_to_empty:
                self._fallback = True
                logger.warning(
                    "[git-authors-plugin] Unable to find a git directory and/or git is not installed."
                    " Option 'fallback_to_empty' set to 'true': Falling back to empty authors list"
                )
            else:
                raise

    def on_files(self, files: Files, /, *, config: MkDocsConfig) -> Union[Files, None]:
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
        if not self._is_enabled():
            return
        if self._fallback:
            return

        for file in files:
            # Exclude pages specified in config
            excluded_pages = self.config.exclude or []
            if exclude(file.src_path, excluded_pages):
                continue

            path = file.abs_src_path
            if path.endswith(".md"):
                _ = self.repo().page(path)

    def on_page_content(
        self, html: str, /, *, page: Page, config: MkDocsConfig, files: Files
    ) -> Union[str, None]:
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
        if not self._is_enabled():
            return html

        # Exclude pages specified in config
        excluded_pages = self.config.exclude or []
        if exclude(page.file.src_path, excluded_pages):
            return html

        # Replace {{ git_site_authors }}
        list_pattern = re.compile(
            r"\{\{\s*git_site_authors\s*\}\}", flags=re.IGNORECASE
        )
        if list_pattern.search(html):
            html = list_pattern.sub(
                ""
                if self._fallback
                else util.site_authors_summary(self.repo().get_authors(), self.config),
                html,
            )

        # Replace {{ git_page_authors }}
        if self._fallback:
            page_authors = ""
        else:
            page_obj = self.repo().page(page.file.abs_src_path)
            page_authors = util.page_authors_summary(page_obj, self.config)

        list_pattern = re.compile(
            r"\{\{\s*git_page_authors\s*\}\}", flags=re.IGNORECASE
        )
        if list_pattern.search(html):
            html = list_pattern.sub(page_authors, html)

        return html

    def on_page_context(
        self,
        context: TemplateContext,
        /,
        *,
        page: Page,
        config: MkDocsConfig,
        nav: Navigation,
    ) -> Union[TemplateContext, None]:
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
        if not self._is_enabled():
            return context
        if self._fallback:
            return context

        # Exclude pages specified in config
        excluded_pages = self.config.exclude or []
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

        return context

    def repo(self) -> Union[Repo, None]:
        """
        Reference to the Repo object of the current project.
        """
        return self._repo

    def _is_enabled(self) -> bool:
        """
        Consider this plugin to be disabled in the following two conditions:
        * config.enabled is false
        * config.enabled is true and
          config.enabled_on_serve is false and
          executed via `serve` command
        """
        is_enabled = True

        if not self.config.enabled:
            is_enabled = False
        elif self.is_serve and not self.config.enabled_on_serve:
            is_enabled = False

        return is_enabled
