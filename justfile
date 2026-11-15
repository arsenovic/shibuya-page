# List the recipes.
default:
    @just --list

# Check that every look sets every variable the layout uses.
test:
    uv run pytest

# Build the demo, reasonable-docs-template in every look, from the template beside this repo.
demo template="../reasonable-docs-template":
    cd {{template}} && uv run --group docs python {{justfile_directory()}}/demo/build.py . {{justfile_directory()}}/_demo/site

# Serve the demo at http://127.0.0.1:8000.
serve-demo: demo
    uv run python -m http.server 8000 --bind 127.0.0.1 --directory _demo/site
