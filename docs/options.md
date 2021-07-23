# Options

You can customize the plugin by setting options in your `mkdocs.yml` file. Here is an example of all the options this plugin offers:

```yaml
plugins:
    - git-authors:
        show_contribution: true
        show_line_count: true
        count_empty_lines: true
        fallback_to_empty: false
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

## `count_empty_lines`

If this option is set to `true` (default: `false`) empty lines will count towards an authors' contribution.

## `fallback_to_empty`

If this option is set to `true` (default: `false`) the plugin will work even outside of a proper Git environment, prompting a warning when it's the case, and resulting in empty author list.
