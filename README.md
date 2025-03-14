[![Actions Status](https://github.com/timvink/mkdocs-git-authors-plugin/workflows/pytest/badge.svg)](https://github.com/timvink/mkdocs-git-authors-plugin/actions)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkdocs-git-authors-plugin)
![PyPI](https://img.shields.io/pypi/v/mkdocs-git-authors-plugin)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mkdocs-git-authors-plugin)
[![codecov](https://codecov.io/gh/timvink/mkdocs-git-authors-plugin/branch/master/graph/badge.svg)](https://codecov.io/gh/timvink/mkdocs-git-authors-plugin)
![GitHub contributors](https://img.shields.io/github/contributors/timvink/mkdocs-git-authors-plugin)
![PyPI - License](https://img.shields.io/pypi/l/mkdocs-git-authors-plugin)

# mkdocs-git-authors-plugin

Lightweight [MkDocs](https://www.mkdocs.org/) plugin to display git authors of a markdown page:

> Authors: Jane Doe, John Doe

See the [demo](https://timvink.github.io/mkdocs-git-authors-plugin/). The plugin only considers authors of the current lines in the page ('surviving code' using `git blame`).

Other MkDocs plugins that use information from git:

- [mkdocs-git-revision-date-localized-plugin](https://github.com/timvink/mkdocs-git-revision-date-localized-plugin) for displaying the last revision date
- [mkdocs-git-committers-plugin](https://github.com/byrnereese/mkdocs-git-committers-plugin) for displaying authors' github user profiles

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

You can then use the `{{ git_page_authors }}` tag in your markdown document, or choose to customize your mkdocs theme (see [usage](https://timvink.github.io/mkdocs-git-authors-plugin/usage.html) page in the docs).

### Note when using build environments

This plugin needs access to the last commit that touched a specific file to be able to retrieve the date. By default many build environments only retrieve the last commit, which means you might need to:
<details>
  <summary>Change your CI settings</summary>
  
  - github actions: set `fetch_depth` to `0` ([docs](https://github.com/actions/checkout))
  - gitlab runners: set `GIT_DEPTH` to `0` ([docs](https://docs.gitlab.com/ee/ci/pipelines/settings.html#limit-the-number-of-changes-fetched-during-clone))
  - bitbucket pipelines: set `clone: depth: full` ([docs](https://support.atlassian.com/bitbucket-cloud/docs/configure-bitbucket-pipelinesyml/))
</details>


## Documentation

See [timvink.github.io/mkdocs-git-authors-plugin](https://timvink.github.io/mkdocs-git-authors-plugin/)

## Contributing

Very much open to contributions! Please read [contributing guide](https://timvink.github.io/mkdocs-git-authors-plugin/contributing.html) before putting in any work.
