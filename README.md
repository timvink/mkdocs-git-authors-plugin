[![Actions Status](https://github.com/timvink/mkdocs-git-authors-plugin/workflows/pytest/badge.svg)](https://github.com/timvink/mkdocs-git-authors-plugin/actions)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-git-authors-plugin)
![PyPI](https://img.shields.io/pypi/v/mkdocs-git-authors-plugin)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mkdocs-git-authors-plugin)
[![codecov](https://codecov.io/gh/timvink/mkdocs-git-authors-plugin/branch/master/graph/badge.svg)](https://codecov.io/gh/timvink/mkdocs-git-authors-plugin)
 
# mkdocs-git-authors-plugin

[MkDocs](https://www.mkdocs.org/) plugin to display git authors of a page. Only considers authors of the current lines in the page ('surviving code' using `git blame`).

Other MkDocs plugins that use information from git:

- [mkdocs-git-committers-plugin](https://github.com/byrnereese/mkdocs-git-committers-plugin) for displaying authors' github user profiles
- [mkdocs-git-revision-date-localized-plugin](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin) for displaying the last revision date

## Setup

Install the plugin using pip:

```bash
pip install mkdocs-git-authors-plugin
```

Activate the plugin in `mkdocs.yml`:

```yaml
plugins:
  - git-authors
```

## Usage

### In supported themes

no supported themes *yet*

### In markdown pages

You can use ``{{ git_authors_summary }}`` to insert a summary of the authors of a page. Authors are sorted by their name and have a `mailto:` link with their email. 

An example output:

```html
<span class='git-authors'><a href='mailto:jane@abc.com'>Jane Doe</a><a href='mailto:john@abc.com'>John Doe</a></span>
```

Which renders as:

> [Jane Doe](mailto:#), [John Doe](mailto:#)

### In theme templates

In theme templates you will have access to the jinja2 variable `git_authors`, which contains a list of authors dicts, like the following example:

```python
[{
    'name' : 'Jane Doe',
    'email' : 'jane@abc.com',
    'last_datetime' : datetime.datetime(),
    'lines' : 200,
    'contribution' : '40.0%'
},
{
    'name' : 'John Doe',
    'email' : 'john@abc.com',
    'last_datetime' : datetime.datetime(),
    'lines' : 300,
    'contribution' : '60.0%'
}]
```

An example of how to use in your templates:

```django hljs
{% if git_authors %}
  {%- for author in git_authors -%}
    <a href="{{ author.email }}" title="{{ author.name }}">
      {{ author.name }}
    </a>,
  {%- endfor -%}
{% endif %}
```

Alternatively, you could use the simple preformatted ``{{ git_authors_summary }}`` to insert a summary of the authors.
