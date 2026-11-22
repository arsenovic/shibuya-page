"""The Fold code button sits above the right sidebar's table of contents, on pages with code only."""

from pathlib import Path

import pytest
from sphinx.application import Sphinx

PAGES = {
    "index": "Home\n====\n\n.. toctree::\n\n   code\n   prose\n",
    "code": "Code\n====\n\nSection\n-------\n\n.. code-block:: python\n\n   print(1)\n",
    "prose": "Prose\n=====\n\nNo code here.\n",
}


def build(tmp_path: Path, **options) -> Path:
    src = tmp_path / "src"
    src.mkdir()
    (src / "conf.py").write_text(
        f'extensions = ["shibuya_page"]\nhtml_theme = "shibuya-page"\nhtml_theme_options = {options!r}\n'
    )
    for name, text in PAGES.items():
        (src / f"{name}.rst").write_text(text)
    out = tmp_path / "html"
    Sphinx(src, src, out, tmp_path / "doctrees", "html", status=None, warningiserror=True).build()
    return out


@pytest.fixture(scope="module")
def site(tmp_path_factory) -> Path:
    return build(tmp_path_factory.mktemp("site"))


def test_button_above_the_toc_on_a_page_with_code(site):
    html = (site / "code.html").read_text()
    assert 'class="sp-fold-code"' in html
    assert html.index('class="sp-fold-code"') < html.index('class="localtoc"')
    assert "shibuya-page/fold-code.js" in html


def test_no_button_on_a_page_without_code(site):
    assert 'class="sp-fold-code"' not in (site / "prose.html").read_text()


def test_option_turns_it_off(tmp_path):
    html = (build(tmp_path, fold_code=False) / "code.html").read_text()
    assert 'class="sp-fold-code"' not in html
    assert "fold-code.js" not in html


def test_bars_are_written_before_each_code_block(site):
    html = (site / "code.html").read_text()
    bar = '<button type="button" class="sp-code-bar" aria-expanded="false">Code · 1 line</button>'
    assert bar in html
    assert html.index(bar) < html.index('class="highlight-python')


def test_head_folds_the_page_before_it_is_drawn(site):
    html = (site / "code.html").read_text()
    head = html[: html.index("</head>")]
    assert "sp-code-folded" in head
    assert "sp-code-folded" not in (site / "prose.html").read_text().split("</head>")[0]
