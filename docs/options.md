# Options

You can customize the plugin by setting options in your `mkdocs.yml` file. Here is an example of all the options this plugin offers:

```yaml
plugins:
    - git-authors:
        show_contribution: true
        show_line_count: true
        show_email_address: true
        count_empty_lines: true
        fallback_to_empty: false
        exclude:
            - index.md
        enabled: true
```

## `show_contribution`

If this option is set to `true` (default: `false`) the contribution of a author is
printed as a percentage of (source file) lines per author. The output is
suppressed if there is only *one* author for a page.

Example output:

* Authors: [John Doe](#) (33.33%), [Jane Doe](#) (66.67%) *(more than one author)*
* Authors: [John Doe](#) *(one author)*

## `show_line_count`

If this option is set to `true` (default: `false`) the number of lines per author is shown.

## `show_email_address`

If this option is set to `true` (default: `true`), then authors' names
are rendered as a `mailto:` link pointing to their email address. If
set to `false`, they are shown in plain text.

## `count_empty_lines`

If this option is set to `true` (default: `false`) empty lines will count towards an authors' contribution.

## `fallback_to_empty`

If this option is set to `true` (default: `false`) the plugin will work even outside of a proper Git environment, prompting a warning when it's the case, and resulting in empty author list.

## `exclude`

Default is empty. Specify a list of page source paths (one per line) that should not have author(s) included (excluded from processing by this plugin). This can be useful for example to remove the authors from the front page. The source path of a page is relative to your `docs/` folder. You can also use [globs](https://docs.python.org/3/library/glob.html) instead of full source paths. To exclude `docs/subfolder/page.md` specify in your `mkdocs.yml` a line under `exclude:` with `- subfolder/page.md`. Some examples:

```yaml
# mkdocs.yml
plugins:
  - git-authors:
      exclude:
        - index.md
        - subfolder/page.md
        - another_page.md
        - folder/*
```

## `enabled`

Default is `true`. Enables you to deactivate this plugin. A possible use case is local development where you might want faster build times and/or do not have git available. It's recommended to use this option with an environment variable together with a default fallback (introduced in `mkdocs` v1.2.1, see [docs](https://www.mkdocs.org/user-guide/configuration/#environment-variables)). Example:

```yaml
# mkdocs.yml
plugins:
  - git-authors:
      enabled: !ENV [ENABLED_GIT_AUTHORS, True]
```

Which enables you do disable the plugin locally using:

```bash
export ENABLED_GIT_AUTHORS=false
mkdocs serve
```
