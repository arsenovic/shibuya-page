"""notebook_figures: notebook kernels started by the build draw matplotlib's figures as SVG (or as set)."""

import os
import sys
import types
from pathlib import Path

import pytest
from sphinx.application import Sphinx

from shibuya_page import NOTEBOOK_STARTUP

VARS = ("PYTHONSTARTUP", "SHIBUYA_PAGE_PREVIOUS_PYTHONSTARTUP", "SHIBUYA_PAGE_FIGURE_FORMATS")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in VARS:
        monkeypatch.delenv(name, raising=False)


def build(tmp_path: Path, **options) -> None:
    src = tmp_path / "src"
    src.mkdir(parents=True)
    (src / "conf.py").write_text(
        f'extensions = ["shibuya_page"]\nhtml_theme = "shibuya-page"\nhtml_theme_options = {options!r}\n'
    )
    (src / "index.rst").write_text("Home\n====\n")
    Sphinx(src, src, tmp_path / "html", tmp_path / "doctrees", "html", status=None, warningiserror=True).build()


def test_svg_by_default(tmp_path):
    build(tmp_path)
    assert os.environ["PYTHONSTARTUP"] == str(NOTEBOOK_STARTUP)
    assert os.environ["SHIBUYA_PAGE_FIGURE_FORMATS"] == "svg"


def test_a_list(tmp_path):
    build(tmp_path, notebook_figures=["svg", "pdf"])
    assert os.environ["SHIBUYA_PAGE_FIGURE_FORMATS"] == "svg,pdf"


def test_keeps_an_earlier_startup_file(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONSTARTUP", "/my/startup.py")
    build(tmp_path)
    assert os.environ["SHIBUYA_PAGE_PREVIOUS_PYTHONSTARTUP"] == "/my/startup.py"


def test_off_puts_the_earlier_one_back(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONSTARTUP", "/my/startup.py")
    build(tmp_path / "a")
    build(tmp_path / "b", notebook_figures="")
    assert os.environ["PYTHONSTARTUP"] == "/my/startup.py"
    assert "SHIBUYA_PAGE_FIGURE_FORMATS" not in os.environ


def test_off_leaves_nothing_set(tmp_path):
    build(tmp_path, notebook_figures="")
    assert not any(name in os.environ for name in VARS)


def test_startup_sets_the_formats_and_runs_the_earlier_one(tmp_path, monkeypatch):
    calls = []
    shell = types.SimpleNamespace(run_line_magic=lambda *args: calls.append(args))
    monkeypatch.setitem(sys.modules, "IPython", types.SimpleNamespace(get_ipython=lambda: shell))
    earlier = tmp_path / "earlier.py"
    earlier.write_text("ran_earlier = True\n")
    monkeypatch.setenv("SHIBUYA_PAGE_FIGURE_FORMATS", "svg,pdf")
    monkeypatch.setenv("SHIBUYA_PAGE_PREVIOUS_PYTHONSTARTUP", str(earlier))
    namespace: dict = {}
    exec(compile(NOTEBOOK_STARTUP.read_text(), str(NOTEBOOK_STARTUP), "exec"), namespace)
    assert calls == [("config", "InlineBackend.figure_formats = ['svg', 'pdf']")]
    assert namespace.get("ran_earlier") is True
    # nothing of its own left in the notebook's namespace
    assert set(namespace) - {"__builtins__"} == {"ran_earlier"}
