# Run by each notebook kernel the docs build starts, as its PYTHONSTARTUP, when shibuya-page's
# notebook_figures option is set: matplotlib's inline figures are drawn in those formats. A notebook
# can still choose its own, with %config InlineBackend.figure_formats. Then runs any PYTHONSTARTUP set
# before. It runs in the notebook's namespace, so it leaves no names behind (comments, not a
# docstring, for that reason: a docstring would set __doc__).


def _shibuya_page_startup() -> None:
    import os

    formats = [f.strip() for f in os.environ.get("SHIBUYA_PAGE_FIGURE_FORMATS", "").split(",") if f.strip()]
    if formats:
        try:
            from IPython import get_ipython

            shell = get_ipython()
            if shell is not None:
                shell.run_line_magic("config", f"InlineBackend.figure_formats = {formats!r}")
        except Exception:  # not IPython, or no inline backend: nothing to set
            pass
    previous = os.environ.get("SHIBUYA_PAGE_PREVIOUS_PYTHONSTARTUP", "")
    if previous and os.path.isfile(previous):
        with open(previous) as f:
            exec(compile(f.read(), previous, "exec"), globals())


_shibuya_page_startup()
del _shibuya_page_startup
