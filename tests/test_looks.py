"""Every look sets every --sp-* variable the theme's stylesheets use, so any look fits the layout."""

import re
from pathlib import Path

import pytest

import shibuya_page

PACKAGE = Path(shibuya_page.__file__).parent
STATIC = PACKAGE / "theme" / "static" / "shibuya-page"
LOOKS = STATIC / "looks"
# the stylesheets every look is drawn with; variables used with a fallback, var(--sp-x, ...), are optional
SHARED = [*STATIC.glob("*.css"), PACKAGE / "static" / "shibuya-page-gallery.css"]


def used(css: str) -> set[str]:
    return set(re.findall(r"var\((--sp-[\w-]+)\)", css))


def defined(css: str, selector: str) -> set[str]:
    block = re.search(re.escape(selector) + r"\s*\{(.*?)\n\}", css, re.S)
    return set(re.findall(r"^\s*(--sp-[\w-]+)\s*:", block.group(1), re.M)) if block else set()


def test_every_look_has_a_stylesheet():
    assert {p.stem for p in LOOKS.glob("*.css")} == set(shibuya_page.LOOKS)


@pytest.mark.parametrize("look", sorted(shibuya_page.LOOKS))
def test_look_sets_every_variable(look):
    css = (LOOKS / f"{look}.css").read_text()
    layout_defaults = defined((STATIC / "layout.css").read_text(), ":root")
    needed = set().union(*(used(p.read_text()) for p in SHARED)) | used(css)
    missing = needed - layout_defaults - defined(css, ":root")
    assert not missing, f"{look}.css doesn't set {sorted(missing)}"


@pytest.mark.parametrize("look", sorted(shibuya_page.LOOKS))
def test_dark_mode_only_changes_variables_the_look_sets(look):
    css = (LOOKS / f"{look}.css").read_text()
    stray = defined(css, "html.dark") - defined(css, ":root")
    assert not stray, f"{look}.css sets {sorted(stray)} only in dark mode"
