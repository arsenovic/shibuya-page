"""A thumbnail gallery of pages: a toctree drawn as a grid of cards.

Works like nbsphinx's ``nbgallery``, for pages from any parser, MyST-NB notebooks included.
MyST-NB has no gallery of its own yet; when it does, prefer it:
https://github.com/executablebooks/MyST-NB/issues/396

Each card's image is, in order of preference:

1. the page's ``thumbnail`` front matter (or ``:thumbnail:`` field), a path relative to the page;
2. the first image in a notebook cell tagged ``thumbnail``;
3. the page's last image, so a notebook's last plot.

A page without one gets an empty tile, which ``--sp-gallery-placeholder`` can fill.
"""

from pathlib import Path
from typing import Any

from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.directives.other import TocTree
from sphinx.environment import BuildEnvironment
from sphinx.util import logging

from . import __version__

STATIC_PATH = Path(__file__).parent / "static"
THUMBNAIL_TAG = "tag_thumbnail"

logger = logging.getLogger(__name__)


class gallery(nodes.General, nodes.Element):
    """Where a gallery's cards go; replaced once every page's thumbnail is known."""


class Gallery(TocTree):
    """``toctree``, with its options, drawn as cards. The toctree stays, hidden, for the sidebar."""

    def run(self) -> list[nodes.Node]:
        result = super().run()
        for toctree in result[0].findall(addnodes.toctree):
            toctree["hidden"] = True
            node = gallery(caption=toctree.get("caption"), entries=list(toctree["entries"]))
            self.env.sp_gallery_pages.setdefault(self.env.docname, set()).update(
                ref for _, ref in toctree["entries"] if ref in self.env.found_docs
            )
            result.append(node)
        return result


def _image_key(env: BuildEnvironment, node: nodes.image) -> str | None:
    """The image's path from the source directory, as Sphinx tracks it, if it's a local file."""
    candidate = node.get("candidates", {}).get("*")
    return candidate if candidate in env.images else None


def _find_thumbnail(app: Sphinx, doctree: nodes.document) -> None:
    env = app.env
    docname = env.docname
    thumbnail = env.metadata.get(docname, {}).get("thumbnail")
    if thumbnail:
        relpath, abspath = env.relfn2path(str(thumbnail), docname)
        if not Path(abspath).is_file():
            logger.warning("thumbnail %r not found", thumbnail, location=docname)
        else:
            # so the builder copies it, as it would an image on the page
            env.images.add_file(docname, relpath)
            env.note_dependency(abspath, docname=docname)
            env.sp_gallery_thumbs[docname] = relpath
            return

    images = [key for node in doctree.findall(nodes.image) if (key := _image_key(env, node))]
    tagged = [
        key
        for cell in doctree.findall(nodes.container)
        if THUMBNAIL_TAG in cell.get("classes", ())
        for node in cell.findall(nodes.image)
        if (key := _image_key(env, node))
    ]
    if tagged or images:
        env.sp_gallery_thumbs[docname] = (tagged or images[::-1])[0]


def _card(app: Sphinx, fromdoc: str, title: str | None, ref: str) -> nodes.Node:
    env = app.env
    if title is None:
        title = env.titles[ref].astext() if ref in env.titles else ref
    link = nodes.reference("", "", internal=True, refuri=app.builder.get_relative_uri(fromdoc, ref))
    thumb = env.sp_gallery_thumbs.get(ref)
    if thumb:
        # candidates, so the builder copies the image and points the page at the copy
        frame = nodes.inline("", "", classes=["sp-gallery-image"])
        frame += nodes.image(uri=thumb, candidates={"*": thumb}, alt="")
    else:
        frame = nodes.inline("", "", classes=["sp-gallery-image", "sp-gallery-empty"])
    link += frame
    link += nodes.inline(title, title, classes=["sp-gallery-title"])
    return nodes.paragraph("", "", link, classes=["sp-gallery-card"])


def _draw_galleries(app: Sphinx, doctree: nodes.document, docname: str) -> None:
    for node in list(doctree.findall(gallery)):
        if app.builder.format != "html":
            node.parent.remove(node)
            continue
        grid = nodes.container(classes=["sp-gallery"])
        if node["caption"]:
            grid += nodes.paragraph(node["caption"], node["caption"], classes=["caption"])
        for title, ref in node["entries"]:
            if ref in app.env.found_docs:
                grid += _card(app, docname, title, ref)
        node.replace_self(grid)


def _init_env(app: Sphinx) -> None:
    env = app.env
    for attr in ("sp_gallery_thumbs", "sp_gallery_pages"):
        if not hasattr(env, attr):
            setattr(env, attr, {})


def _purge(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    env.sp_gallery_thumbs.pop(docname, None)
    env.sp_gallery_pages.pop(docname, None)


def _merge(app: Sphinx, env: BuildEnvironment, docnames: set[str], other: BuildEnvironment) -> None:
    for docname in docnames:
        if docname in other.sp_gallery_thumbs:
            env.sp_gallery_thumbs[docname] = other.sp_gallery_thumbs[docname]
        if docname in other.sp_gallery_pages:
            env.sp_gallery_pages[docname] = other.sp_gallery_pages[docname]


def _outdated(
    app: Sphinx, env: BuildEnvironment, added: set[str], changed: set[str], removed: set[str]
) -> list[str]:
    """A gallery is rebuilt when one of its pages changes, since that can change its thumbnail."""
    touched = added | changed | removed
    return [page for page, refs in env.sp_gallery_pages.items() if refs & touched]


def _add_static(app: Sphinx, config: Any) -> None:
    config.html_static_path.append(str(STATIC_PATH))


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_node(gallery)
    app.add_directive("gallery", Gallery)
    app.connect("builder-inited", _init_env)
    app.connect("config-inited", _add_static)
    # after Sphinx's image collector (500) has registered the page's images
    app.connect("doctree-read", _find_thumbnail, priority=600)
    app.connect("doctree-resolved", _draw_galleries)
    app.connect("env-purge-doc", _purge)
    app.connect("env-merge-info", _merge)
    app.connect("env-get-outdated", _outdated)
    app.add_css_file("shibuya-page-gallery.css")
    return {"version": __version__, "parallel_read_safe": True, "parallel_write_safe": True, "env_version": 1}
