from mkdocs.config import config_options
from mkdocs.config.base import Config


class GitAuthorsPluginConfig(Config):
    show_contribution = config_options.Type(bool, default=False)
    show_line_count = config_options.Type(bool, default=False)
    show_email_address = config_options.Type(bool, default=True)
    href = config_options.Type(str, default="mailto:{email}")
    count_empty_lines = config_options.Type(bool, default=True)
    fallback_to_empty = config_options.Type(bool, default=False)
    exclude = config_options.Type(list, default=[])
    ignore_commits = config_options.Type(str, default="")
    ignore_authors = config_options.Type(list, default=[])
    enabled = config_options.Type(bool, default=True)
    enabled_on_serve = config_options.Type(bool, default=True)
    sort_authors_by = config_options.Type(str, default="name")
    authorship_threshold_percent = config_options.Type(int, default=0)
    strict = config_options.Type(bool, default=True)
    # sort_authors_by_name = config_options.Type(bool, default=True)
    # sort_reverse = config_options.Type(bool, default=False)
