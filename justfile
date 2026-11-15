# List the recipes.
default:
    @just --list

# Check that every look sets every variable the layout uses.
test:
    uv run pytest

# Build the demo, reasonable-docs-template in every look with a switcher, from the template beside this repo.
demo template="../reasonable-docs-template":
    cd {{template}} && uv run --group docs python -m shibuya_page.looks docs {{justfile_directory()}}/_demo/site -W

# Build the demo and serve it at http://127.0.0.1:8000.
serve-demo template="../reasonable-docs-template":
    cd {{template}} && uv run --group docs python -m shibuya_page.looks docs {{justfile_directory()}}/_demo/site -W --serve
