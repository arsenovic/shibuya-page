// The "Fold code" button above the right sidebar's table of contents folds every code block on the page
// (outputs stay) into the bar written before it at build time; a bar opens just its block. The choice
// holds across pages. A script in <head> folds the page before it's drawn, so this one only handles clicks.
(() => {
  const KEY = "sp-fold-code";
  const root = document.documentElement;
  const bars = () => document.querySelectorAll(".yue .sp-code-bar");

  const show = (button, folded) => {
    root.classList.toggle("sp-code-folded", folded);
    button.setAttribute("aria-pressed", String(folded));
    // folding or unfolding the page closes the blocks opened one at a time
    for (const bar of bars()) bar.setAttribute("aria-expanded", "false");
  };

  const init = () => {
    const button = document.querySelector(".sp-fold-code");
    if (!button) return;
    show(button, root.classList.contains("sp-code-folded"));
    button.addEventListener("click", () => {
      const folded = !root.classList.contains("sp-code-folded");
      try {
        localStorage.setItem(KEY, folded ? "folded" : "open");
      } catch {}
      show(button, folded);
    });
    for (const bar of bars()) {
      bar.addEventListener("click", () => {
        bar.setAttribute("aria-expanded", String(bar.getAttribute("aria-expanded") !== "true"));
      });
    }
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
