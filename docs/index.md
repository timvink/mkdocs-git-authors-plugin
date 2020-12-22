# mkdocs-git-authors-plugin

Lightweight MkDocs plugin to display git authors of a markdown page.

## Setup

Install the plugin using pip3:

```bash
pip3 install mkdocs-git-authors-plugin
```

Next, add the following lines to your `mkdocs.yml`:

```yaml
plugins:
  - search
  - git-authors
```

> If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set.

!!! warning "Using build environments"

    This plugin needs access to the last commit that touched a specific file to be able to retrieve the date. By default many build environments only retrieve the last commit, which means you might need to:

    **Change your CI settings**

    - github actions: set `fetch_depth` to `0` ([docs](https://github.com/actions/checkout))
    - gitlab runners: set `GIT_DEPTH` to `1000` ([docs](https://docs.gitlab.com/ee/user/project/pipelines/settings.html#git-shallow-clone))
    - bitbucket pipelines: set `clone: depth: full` ([docs](https://support.atlassian.com/bitbucket-cloud/docs/configure-bitbucket-pipelinesyml/))

