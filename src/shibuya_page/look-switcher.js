// The look switcher that `python -m shibuya_page.looks` adds: a menu in the corner that opens this page
// in another look. Each look is a copy of the site in its own folder, /<look>/, so switching swaps that part of the address.
(() => {
  const parts = location.pathname.split("/");
  const at = parts.findIndex((part) => SP_LOOKS.includes(part));
  if (at < 0) return;

  const box = document.createElement("label");
  box.className = "sp-look-switcher";
  box.textContent = "Look ";
  const menu = document.createElement("select");
  for (const look of SP_LOOKS) {
    menu.add(new Option(look, look, false, look === parts[at]));
  }
  menu.addEventListener("change", () => {
    parts[at] = menu.value;
    location.href = parts.join("/") + location.search + location.hash;
  });
  box.append(menu);

  const style = document.createElement("style");
  style.textContent = `
    .sp-look-switcher {
      position: fixed; left: 1rem; bottom: 1rem; z-index: 100;
      display: flex; align-items: center; gap: 0.5rem;
      padding: 0.4rem 0.6rem 0.4rem 0.8rem; border-radius: 999px;
      background: var(--sp-nav-bg); color: var(--sp-nav-text);
      font: 600 0.85rem var(--sp-font-text); box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    }
    .sp-look-switcher select {
      font: inherit; padding: 0.15rem 0.4rem; border-radius: 999px; border: 0;
      background: var(--sp-page); color: var(--sp-text);
    }`;
  document.head.append(style);
  document.body.append(box);
})();
