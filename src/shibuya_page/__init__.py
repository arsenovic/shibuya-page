"""shibuya-page: the Shibuya Sphinx theme, laid out as a sheet of paper on a desk."""

import posixpath
from pathlib import Path
from typing import Any

from sphinx.application import Sphinx
from sphinx.util import logging

__version__ = "0.1.0"

THEME_PATH = Path(__file__).parent / "theme"

LATO_ROBOTO = (
    "https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;700;900"
    "&family=Lato:ital,wght@0,400;0,700;1,400&family=Roboto+Mono:wght@400;700&display=swap"
)

# Each look is theme/static/shibuya-page/looks/<name>.css, which sets every --sp-* variable; the
# stylesheet that loads the fonts it names ("" for system fonts); and, optionally, the Pygments styles
# for code in light and dark mode, in place of the theme's. To add one, add its stylesheet and an
# entry here; tests/test_looks.py checks it.
LOOKS: dict[str, dict[str, Any]] = {
    "rtd": {"webfonts": LATO_ROBOTO},
    "alabaster": {"webfonts": LATO_ROBOTO},
    # pydata-sphinx-theme's docs (and NumPy's and SciPy's), in system fonts
    "pydata": {"webfonts": "", "pygments": ("a11y-high-contrast-light", "a11y-high-contrast-dark")},
}

logger = logging.getLogger(__name__)


def _flag(value: Any) -> bool:
    """A theme option as a bool: theme.toml gives strings, conf.py may give either."""
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes", "on")
    return bool(value)


def _uses_theme(app: Sphinx) -> bool:
    """Whether the HTML theme is this one, or a theme that inherits from it."""
    theme = getattr(app.builder, "theme", None)
    return theme is not None and THEME_PATH in (Path(d) for d in getattr(theme, "_dirs", ()))


def _options(app: Sphinx) -> dict[str, Any]:
    return app.builder.theme.get_options(app.builder.theme_options)


def _set_look_pygments(app: Sphinx) -> None:
    """Give the theme the look's Pygments styles, before Shibuya reads them to build its highlighter."""
    if not _uses_theme(app):
        return
    styles = LOOKS.get(_options(app)["look"], {}).get("pygments")
    if styles:
        app.builder.theme.pygments_style_default, app.builder.theme.pygments_style_dark = styles


def _on_builder_inited(app: Sphinx) -> None:
    if not _uses_theme(app):
        return
    options = _options(app)
    look = options["look"]
    if look in LOOKS:
        # after the theme's layout (200), before the project's own html_css_files (800)
        app.add_css_file(f"shibuya-page/looks/{look}.css", priority=300)
    elif look != "none":
        logger.warning("shibuya-page: unknown look %r; use one of %s, or 'none'", look, ", ".join(LOOKS))
    webfonts = options["webfonts"]
    if webfonts == "auto":
        webfonts = LOOKS.get(look, {}).get("webfonts", "")
    if webfonts:
        app.add_css_file(webfonts, priority=300)
    if _flag(options["prune_page_headings"]):
        app.add_css_file("shibuya-page/prune-page-headings.css", priority=300)
    if _flag(options["external_links_new_tab"]):
        app.add_js_file("shibuya-page/external-links.js")


def _is_notebook(app: Sphinx, pagename: str, context: dict[str, Any]) -> bool:
    if context.get("page_source_suffix") == ".ipynb":
        return True
    # a MyST (jupytext) notebook names its kernel in its front matter
    return "kernelspec" in app.env.metadata.get(pagename, {})


def _on_page_context(
    app: Sphinx, pagename: str, templatename: str, context: dict[str, Any], doctree: Any
) -> None:
    context["sp_download"] = None
    if doctree is None or not _uses_theme(app) or not _flag(_options(app)["download_notebooks"]):
        return
    sourcename = context.get("sourcename")
    if not sourcename or not _is_notebook(app, pagename, context):
        return
    # html_copy_source puts every source under _sources/, as <name><suffix>.txt by default
    context["sp_download"] = {
        "url": context["pathto"](f"_sources/{sourcename}", 1),
        "filename": posixpath.basename(pagename) + context.get("page_source_suffix", ""),
    }


def setup(app: Sphinx) -> dict[str, Any]:
    app.setup_extension("shibuya")
    app.add_html_theme("shibuya-page", str(THEME_PATH))
    # before Shibuya's builder-inited (500), which builds the highlighter from the theme's styles
    app.connect("builder-inited", _set_look_pygments, priority=400)
    app.connect("builder-inited", _on_builder_inited)
    app.connect("html-page-context", _on_page_context)
    return {"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True}
