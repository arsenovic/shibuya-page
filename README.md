# shibuya-page

A [Sphinx](https://www.sphinx-doc.org/) theme: [Shibuya](https://shibuya.lepture.com/), laid out as
a sheet of paper on a desk, in the colors of the read-the-docs or alabaster themes. It's a child
theme, so every Shibuya option still works.

It adds:

- **Palettes**: `rtd` (sphinx_rtd_theme's blues, code and API signatures) and `alabaster`, each
  with a dark mode. Change any color with a CSS variable.
- **Breadcrumbs** above each page, with a **Download** link on notebook pages.
- **A thumbnail gallery** of pages (`shibuya_page.gallery`), for notebooks from MyST-NB or any
  other source.
- **Landing-page classes**: a two-column features list, cards, a figure beside text.
- Styles for **MyST-NB** and **nbsphinx** notebooks, and for links from
  [sphinx-codeautolink](https://sphinx-codeautolink.readthedocs.io/).

For a project set up with it (guides, a gallery of examples, an API reference, and `just` recipes),
start from [reasonable-docs-template](https://github.com/arsenovic/reasonable-docs-template).

## Install

```sh
pip install shibuya-page
```

## Use

In `conf.py`:

```python
html_theme = "shibuya-page"
html_theme_options = {
    "palette": "rtd",
    # any Shibuya option: https://shibuya.lepture.com/customisation/
    "light_logo": "_static/logo.svg",
    "github_url": "https://github.com/you/project",
    "nav_links": [
        {"title": "Guides", "url": "guides/index"},
        {"title": "Examples", "url": "examples/index"},
        {"title": "API", "url": "api/index"},
    ],
}
```

## Options

shibuya-page's options sit beside Shibuya's in `html_theme_options`.

| Option                   | Default         | Effect |
| ------------------------ | --------------- | ------ |
| `palette`                | `"rtd"`         | `"rtd"`, `"alabaster"`, or `"none"` to set every `--sp-*` variable yourself. |
| `webfonts`               | Google Fonts URL for Lato, Roboto Slab and Roboto Mono | A stylesheet that loads the fonts; `""` loads none. Name the fonts with `--sp-font-*`. |
| `prune_page_headings`    | `True`          | The left sidebar leaves out a page's own headings (the right sidebar lists them), but keeps headings that group other pages. |
| `external_links_new_tab` | `True`          | Links that leave the site open in a new tab. |
| `download_notebooks`     | `True`          | Notebook pages get a Download link for their source at the end of the breadcrumbs. Needs `html_copy_source` (on by default). |

The theme also sets Pygments styles, `sphinx` in light mode and `github-dark` in dark mode. Set
`pygments_style` in `conf.py` to choose your own.

## Colors and fonts

Every color is a CSS variable. To change some, add a stylesheet of your own:

```python
html_static_path = ["_static"]
html_css_files = ["custom.css"]
```

```css
/* _static/custom.css */
:root {
  --sp-nav-bg: #1f4e8c;
  --sp-font-heading: "Lato", sans-serif;
}
html.dark {
  --sp-nav-bg: #12304f;
}
```

| Variable | What it colors |
| --- | --- |
| `--sp-desk`, `--sp-page`, `--sp-page-shadow`, `--sp-scroll-thumb` | The desk behind the page, the page, its shadow, and scrollbars |
| `--sp-text`, `--sp-bold`, `--sp-light`, `--sp-foot-text` | Body text, bold text, secondary text, the footer |
| `--sp-link`, `--sp-link-hover`, `--sp-caption` | Links, and the captions over sidebar and toctree groups |
| `--sp-rule`, `--sp-card-border` | Heading rules, and gallery and card borders |
| `--sp-code-block-bg`, `--sp-code-block-text` | Code blocks in light mode (dark mode uses the dark Pygments style) |
| `--sp-code-bg`, `--sp-code-text`, `--sp-code-border` | Inline code |
| `--sp-sidebar-link`, `--sp-sidebar-link-hover` | Sidebar links |
| `--sp-nav-bg`, `--sp-nav-text`, `--sp-nav-hover` | The navbar |
| `--sp-note-*`, `--sp-warn-*`, `--sp-sig-*`, `--sp-member-*` | Admonitions and API signatures, in the palette that styles them |
| `--sp-font-text`, `--sp-font-heading`, `--sp-font-mono` | Fonts |
| `--sp-logo-size`, `--sp-page-radius` | The logo's height, and the page's corners |
| `--sp-gallery-placeholder` | The image on gallery cards for pages without one, such as `url("logo.svg")` |

## Gallery

`shibuya_page.gallery` adds a `gallery` directive: a toctree, with the same options, drawn as a grid
of cards, each a thumbnail over the page's title. The toctree stays, hidden, so the sidebar still
lists the pages.

```python
extensions = [..., "shibuya_page.gallery"]
```

````markdown
## Basics

```{gallery}
:glob:

basics/*
```
````

A card's image is, in order:

1. the page's `thumbnail` front matter (`:thumbnail:` in reStructuredText), a path from the page;
2. the first image in a notebook cell tagged `thumbnail`;
3. the page's last image, so a notebook's last plot.

The gallery works with any parser and any theme, and stands in until MyST-NB has a gallery of its
own ([executablebooks/MyST-NB#396](https://github.com/executablebooks/MyST-NB/issues/396)). nbsphinx's
`nbgallery` also works, drawn as the same cards.

## Landing pages

Classes for a project's home page. Give an element one with `rst-class` (reStructuredText), or
`{.class}` before a block (MyST, with the `attrs_block` extension).

| Class            | On                | Effect |
| ---------------- | ----------------- | ------ |
| `sp-features`    | a bulleted list   | Flows down two columns; items with sublists get bold labels. |
| `sp-side-by-side`| a container       | Its children side by side, text then a figure; stacked on phones. |
| `sp-cards`       | a list-table      | A grid of cards, one per cell, each an image over a caption. |
| `sp-title-image` | a section         | Hides its h1 visually, for a title graphic (`img.sp-title`) in its place. |
| `sp-light-only`, `sp-dark-only` | an image | Shown in one color mode. |
| `sp-invert-dark` | an image          | Black lines on a transparent background turn white in dark mode. |
| `sp-logos`       | a section         | Its images float right of the text beside them. |

An emphasized part of the page title is a subtitle: `# Name *— what it does*`.

## Templates

The theme replaces two of Shibuya's templates: `components/breadcrumbs.html` (a copy of Shibuya
2026.7.12's, with the Download link) and `partials/webfonts.html`. A project's own `_templates`
still win over both.

## Development

```sh
uv sync
```

The [CI](.github/workflows/docs.yml) builds reasonable-docs-template with this theme in each palette,
and against the newest Shibuya every week.

## Licence

BSD-3-Clause
