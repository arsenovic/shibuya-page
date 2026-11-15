# shibuya-page

A [Sphinx](https://www.sphinx-doc.org/) theme: [Shibuya](https://shibuya.lepture.com/), laid out as
a sheet of paper on a desk, in the colors of the read-the-docs or alabaster themes. It's a child
theme, so every Shibuya option still works.

It adds:

- **Looks**: `rtd` (sphinx_rtd_theme's blues, code and API signatures), `alabaster`, `scipy`
  (SciPy's docs: pydata-sphinx-theme's colors, system fonts, underlined links), and `pydata`
  (pydata-sphinx-theme's own docs: the same, in its newer system fonts), each a palette, fonts and
  styling, with a dark mode. Change any color or font with a CSS variable.
  See them all in the [demo](https://arsenovic.github.io/shibuya-page/), which has a switcher.
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
    "look": "rtd",
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
| `look`                   | `"rtd"`         | `"rtd"`, `"alabaster"`, `"scipy"`, `"pydata"`, or `"none"` to set every `--sp-*` variable yourself. |
| `webfonts`               | `"auto"`        | `"auto"` loads the look's fonts. Or a stylesheet URL that loads your own, named with `--sp-font-*`; or `""` for none. |
| `prune_page_headings`    | `True`          | The left sidebar leaves out a page's own headings (the right sidebar lists them), but keeps headings that group other pages. |
| `external_links_new_tab` | `True`          | Links that leave the site open in a new tab. |
| `download_notebooks`     | `True`          | Notebook pages get a Download link for their source at the end of the breadcrumbs. Needs `html_copy_source` (on by default). |

Code is highlighted with the look's Pygments styles: `sphinx` and `github-dark` (light and dark)
for rtd and alabaster, and `a11y-high-contrast-light` and `-dark` for scipy and pydata, as they use. Set
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
| `--sp-note-*`, `--sp-tip-*`, `--sp-warn-*`, `--sp-danger-*` | Admonitions, by type, in the looks that color them |
| `--sp-sig-*`, `--sp-member-*` | API signatures, in the looks that style them |
| `--sp-font-text`, `--sp-font-heading`, `--sp-font-mono` | Fonts |
| `--sp-logo-size`, `--sp-page-radius` | The logo's height, and the page's corners |
| `--sp-gallery-placeholder` | The image on gallery cards for pages without one, such as `url("logo.svg")` |

## Adding a look

A look is one stylesheet, `src/shibuya_page/theme/static/shibuya-page/looks/<name>.css`, and an
entry in `LOOKS` in `src/shibuya_page/__init__.py` naming its fonts and, optionally, its Pygments
styles. The stylesheet sets every
`--sp-*` variable on `:root`, changes the ones it needs under `html.dark`, and may restyle code,
links, headings and admonitions. Copying `rtd.css` is the easiest start.

`just test` checks that each look sets every variable the layout uses, and `just demo` builds
reasonable-docs-template in every look, with a switcher, into `_demo/site` (`just serve-demo` serves
it). The CI publishes that demo.

## Choosing a look

To see your own docs in every look, with a menu in the corner that switches between them:

```sh
python -m shibuya_page.looks docs docs/_build/looks --serve
```

It builds the docs once per look, into `docs/_build/looks/<look>/`, and serves them at
http://127.0.0.1:8000 (`--serve 8001` for another port). Other options, such as `-W`, go to
sphinx-build. Then set the one you like as `look` in `conf.py`.

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
just test
just demo        # needs reasonable-docs-template beside this repo
```

The [CI](.github/workflows/docs.yml) runs the tests, builds the demo against the locked and the
newest Shibuya (weekly too), and publishes it.

## Licence

BSD-3-Clause
