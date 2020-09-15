# Usage

## In supported themes

no supported themes *yet*.

## In markdown pages

You can use the following jinja tags to insert content into your markdown pages:

- <code>\{\{&nbsp;git_page_authors \}\}</code> a summary of the authors of a page. Output wrapped in `<span class='git-page-authors'>`
- <code>\{\{&nbsp;git_site_authors \}\}</code> a summary of all authors of all pages in your site. Output wrapped in `<span class='git-site-authors'>`

For example, adding <code>\{\{ git_page_authors \}\}</code> will insert:

```html
<span class='git-page-authors'><a href='mailto:jane@abc.com'>Jane Doe</a><a href='mailto:john@abc.com'>John Doe</a></span>
```

Which renders as:

> [Jane Doe](mailto:jane@abc.com), [John Doe](mailto:john@abc.com)


## In theme customizations

[MkDocs](https://www.mkdocs.org/) offers possibilities to [customize an existing theme](https://www.mkdocs.org/user-guide/styling-your-docs/#customizing-a-theme).

As an example, if you use [mkdocs-material](https://github.com/squidfunk/mkdocs-material) you can implement git-authors by [overriding a template block](https://squidfunk.github.io/mkdocs-material/customization/#overriding-template-blocks):

1) Create a new file `main.html` in `docs/theme`:

```html
{% extends "base.html" %}

{% block disqus %}
    <div class="md-source-date">
    <small>
        Authors: {{ git_page_authors }}
    </small>
  </div>
    {% include "partials/integrations/disqus.html" %}
{% endblock %}
```

2) In `mkdocs.yml` make sure to specify the custom directory with the theme overrides:

```yml
theme:
    name: material
    custom_dir: docs/theme/
```

## In theme templates

To add more detailed git author information to your theme you can [customize a MkDocs theme](https://www.mkdocs.org/user-guide/styling-your-docs/#customizing-a-theme) or even [develop your own](https://www.mkdocs.org/user-guide/custom-themes/). 

When enabling this plugin, you will have access to the jinja2 variable `git_info` which contains as dict with the following structure:

```python
{
  'page_authors' : [
    {
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
  }
 ],
 'site_authors' : # same structure
}
```

#### Example usage in theme development

An example of how to use in your templates:

```html
{% if git_info %}
  {%- for author in git_info.get('page_authors') -%}
    <a href="{{ author.email }}" title="{{ author.name }}">
      {{ author.name }}
    </a>,
  {%- endfor -%}
{% endif %}
```

Alternatively, you could use the simple pre-formatted `{{ git_page_authors }}` to insert a summary of the authors.
