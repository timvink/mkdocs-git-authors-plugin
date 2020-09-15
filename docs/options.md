# Options

You can customize the plugin by setting options in your `mkdocs.yml` file. Here is an example of all the options this plugin offers:

```yml
plugins:
    - print-site:
        show_contribution: true
        show_line_count: true
        count_empty_lines: true
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
