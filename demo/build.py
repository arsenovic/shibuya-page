"""Build reasonable-docs-template once per look into one site, with a switcher between them.

    python demo/build.py <template-dir> <site-dir>

Each look goes in <site-dir>/<look>/, and <site-dir>/index.html opens the first. The switcher is only
for this demo: it's added to the built pages, and isn't part of the theme.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import shibuya_page

HERE = Path(__file__).parent


def main(template: Path, site: Path) -> None:
    looks = list(shibuya_page.LOOKS)
    work = site.parent / f"{site.name}-work"
    shutil.rmtree(site, ignore_errors=True)
    for look in looks:
        out = work / look / "html"
        subprocess.run(
            [
                sys.executable, "-m", "sphinx", "-W", "--keep-going", "-b", "html",
                "-d", str(work / look / "doctrees"),
                "-D", f"html_theme_options.look={look}",
                # the looks share one cache of executed notebooks, kept out of the site
                "-D", f"nb_execution_cache_path={work / '.jupyter_cache'}",
                str(template / "docs"), str(out),
            ],
            check=True,
        )
        shutil.copytree(out, site / look)

    switcher = (HERE / "look-switcher.js").read_text()
    tag = f"<script>\nconst SP_LOOKS = {json.dumps(looks)};\n{switcher}</script>\n</body>"
    for page in site.rglob("*.html"):
        html = page.read_text()
        if "</body>" in html:
            page.write_text(html.replace("</body>", tag, 1))

    (site / "index.html").write_text(
        f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url={looks[0]}/">'
        f'<link rel="canonical" href="{looks[0]}/"><title>shibuya-page</title>'
    )
    (site / ".nojekyll").touch()


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
