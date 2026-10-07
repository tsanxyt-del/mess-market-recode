/* public search: local UX only (no network — form submits via GET) + match highlight */
document.addEventListener("DOMContentLoaded", () => {
  const input = document.querySelector('input[name="q"]');
  if (input) {
    input.addEventListener("input", window.Utils.debounce(() => {
      const q = input.value.trim();
      // Only a gentle hint — actual results render server-side on submit.
      input.classList.toggle("input-soon", q.length === 1);
    }, 300));
    // Highlight the searched word inside server-rendered result rows.
    try {
      const q = new URLSearchParams(window.location.search).get("q") || "";
      if (q.trim().length >= 2) {
        const esc = q.trim().replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        const rx = new RegExp("(" + esc + ")", "gi");
        document.querySelectorAll(".tbl .rowlink").forEach((cell) => {
          if (cell.querySelector("mark")) return;
          const walker = document.createTreeWalker(cell, NodeFilter.SHOW_TEXT);
          const nodes = [];
          while (walker.nextNode()) nodes.push(walker.currentNode);
          nodes.forEach((node) => {
            const parts = node.textContent.split(rx);
            if (parts.length < 2) return;
            const frag = document.createDocumentFragment();
            parts.forEach((part, i) => {
              if (i % 2 === 1) {
                const m = document.createElement("mark");
                m.textContent = part;
                frag.appendChild(m);
              } else {
                frag.appendChild(document.createTextNode(part));
              }
            });
            node.replaceWith(frag);
          });
        });
      }
    } catch (_) {}
  }
});
