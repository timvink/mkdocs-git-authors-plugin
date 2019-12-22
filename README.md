![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-git-authors-plugin)
![PyPI](https://img.shields.io/pypi/v/mkdocs-git-authors-plugin)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mkdocs-git-authors-plugin)
 
# mkdocs-git-authors-plugin

[MkDocs](https://www.mkdocs.org/) plugin 

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

**no supported themes yet**

### In theme templates

TODO

### In markdown pages

TODO

## Options

### `type`

Set this option to one of:

- `authors`. Default
- `contributors`. TODO
- `current`. via git blame. TODO.

### Example

Example of setting both options:

```yaml
# mkdocs.yml
plugins:
  - git-authors:
    type: contributers
```
