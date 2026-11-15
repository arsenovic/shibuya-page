"""Build a project's docs once per look into one site, with a switcher between them, to choose a look.

    python -m shibuya_page.looks <source-dir> <site-dir> [--serve [PORT]] [sphinx options...]

Each look goes in <site-dir>/<look>/, and <site-dir>/index.html opens the first. Any other options,
such as -W, go to sphinx-build. The switcher is added to the built pages; it isn't part of the theme.
"""

import argparse
import functools
import http.server
import json
import shutil
import subprocess
import sys
from pathlib import Path

from shibuya_page import LOOKS

SWITCHER = Path(__file__).with_name("look-switcher.js")


def build(source: Path, site: Path, sphinx_args: list[str]) -> None:
    looks = list(LOOKS)
    work = site.parent / f"{site.name}-work"
    shutil.rmtree(site, ignore_errors=True)
    for look in looks:
        out = work / look / "html"
        subprocess.run(
            [
                sys.executable, "-m", "sphinx", "--keep-going", "-b", "html",
                "-d", str(work / look / "doctrees"),
                "-D", f"html_theme_options.look={look}",
                # the looks share one cache of executed notebooks, kept out of the site
                "-D", f"nb_execution_cache_path={work / '.jupyter_cache'}",
                *sphinx_args,
                str(source), str(out),
            ],
            check=True,
        )
        shutil.copytree(out, site / look)

    tag = f"<script>\nconst SP_LOOKS = {json.dumps(looks)};\n{SWITCHER.read_text()}</script>\n</body>"
    for page in site.rglob("*.html"):
        html = page.read_text()
        if "</body>" in html:
            page.write_text(html.replace("</body>", tag, 1))

    (site / "index.html").write_text(
        f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={looks[0]}/">'
        f'<link rel="canonical" href="{looks[0]}/"><title>Looks</title>'
    )
    (site / ".nojekyll").touch()


def serve(site: Path, port: int) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=site)
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        print(f"Serving every look at http://127.0.0.1:{port}/ (Ctrl+C stops)", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m shibuya_page.looks", description=__doc__.split("\n")[0])
    parser.add_argument("source", type=Path, help="the docs' source folder, with conf.py")
    parser.add_argument("site", type=Path, help="where to write the site")
    parser.add_argument("--serve", type=int, nargs="?", const=8000, metavar="PORT",
                        help="serve the site afterwards, at http://127.0.0.1:PORT (8000)")
    args, sphinx_args = parser.parse_known_args()
    build(args.source.resolve(), args.site.resolve(), sphinx_args)
    if args.serve is not None:
        serve(args.site.resolve(), args.serve)


if __name__ == "__main__":
    main()
