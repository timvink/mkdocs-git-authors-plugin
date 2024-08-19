# Options

You can customize the plugin by setting options in your `mkdocs.yml` file. Here is an example of all the options this plugin offers:

```yaml
plugins:
    - git-authors:
        show_contribution: true
        show_line_count: true
        show_email_address: true
        href: "mailto:{email}"
        count_empty_lines: true
        fallback_to_empty: false
        sort_authors_by: name
        authorship_threshold_percent: 10
        ignore_authors:
            - john@doe.com
        ignore_commits: .git-blame-ignore-revs
        exclude:
            - index.md
        enabled: true
        enabled_on_serve: true
        strict: true
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
are rendered as (by default) a `mailto:{email}` link pointing to their email address. If
set to `false`, they are shown in plain text.

## `href`

Given `show_email_adress` is set to `true`, you can customize the rendered link with the option `href`
(default: `mailto:{email}`) using the f-string format (available `{email}` and `{name}`).
This is useful to link to IM tools i.e. `href: "https://teams.microsoft.com/l/chat/0/0?users={email}"`.

## `count_empty_lines`

If this option is set to `true` (default: `false`) empty lines will count towards an authors' contribution.

## `fallback_to_empty`

If this option is set to `true` (default: `false`) the plugin will work even outside of a proper Git environment, prompting a warning when it's the case, and resulting in empty author list.

## `exclude`

Default is empty. Specify a list of page source paths (one per line) that should not have author(s) included (excluded from processing by this plugin). This can be useful for example to remove the authors from the front page. The source path of a page is relative to your `docs/` folder. You can also use [globs](https://docs.python.org/3/library/glob.html) instead of full source paths. To exclude `docs/subfolder/page.md` specify in your `mkdocs.yml` a line under `exclude:` with `- subfolder/page.md`. Some examples:

## `ignore_authors`

Default is empty. Specifies a list of emails for authors whose contributions should be ignored by this plugin.

## `ignore_commits`

Default is empty. Specifies a file containing a list of commit hashes (one per line) that should be ignored.  Changes made in these commits will be attributed to the previous commit that changed the line.

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

## `sort_authors_by`

Defaults to `name`, can be `contribution` to sort the authors by contribution percentage without needing to show the exact percent.

## `authorship_threshold_percent`

Default is `0`, allowed values between `0` and `100`. This option sets the minimum contribution percentage for an author to be included in the list of authors. This can be useful when you have a large number of single line authors who contributed minor spelling fixes, and not major content. This option does not apply if there is only one author.

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

## `enabled_on_serve`

Default is `true`. Allows you to deactivate this plugin when `mkdocs` is called with the command `serve`. A possible use case is local development where you might want faster build times and/or do not have git available.

## `strict`

Default is `true`. When enabled, the logs will show warnings when something is wrong but a fallback has been used. When disabled, the logger will use the INFO level instead.

- If you want to raise an error when a warning is logged, use [mkdocs strict mode](https://www.mkdocs.org/user-guide/configuration/#strict) (with `mkdocs build --strict`).
- If you are already using [mkdocs strict mode](https://www.mkdocs.org/user-guide/configuration/#strict), but do not care about these warnings, you can set `strict: false` to ensure no errors are raised.

```yaml
# mkdocs.yml
plugins:
  - git-authors:
      strict: true
```
