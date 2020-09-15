# mkdocs-git-authors-plugin

Lightweight MkDocs plugin to display git authors of a markdown page.

## Setup

Install the plugin using pip3:

```bash
pip3 install mkdocs-git-authors-plugin
```

Next, add the following lines to your `mkdocs.yml`:

```yml
plugins:
  - search
  - git-authors
```

> If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set.
