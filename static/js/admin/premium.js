/* v5.0 admin premium: mobile drawer, menu search, cmdk jump, KPI count-up */
(function () {
  // 1. Mobile drawer
  try {
    var toggle = document.getElementById("sideToggle");
    var overlay = document.getElementById("sideOverlay");
    if (toggle) toggle.addEventListener("click", function () {
      document.body.classList.toggle("side-open");
    });
    if (overlay) overlay.addEventListener("click", function () {
      document.body.classList.remove("side-open");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        document.body.classList.remove("side-open");
        closeCmdk();
      }
    });
  } catch (e) {}

  // 2. Sidebar menu live filter
  try {
    var search = document.getElementById("sideSearch");
    var nav = document.getElementById("sideNav");
    if (search && nav) {
      search.addEventListener("input", function () {
        var q = search.value.trim().toLowerCase();
        var groups = nav.querySelectorAll(".side-group");
        nav.querySelectorAll("a").forEach(function (a) {
          var hit = !q || a.textContent.toLowerCase().indexOf(q) !== -1;
          a.style.display = hit ? "" : "none";
        });
        groups.forEach(function (g) {
          var next = g.nextElementSibling;
          var anyVisible = false;
          while (next && !next.classList.contains("side-group")) {
            if (next.tagName === "A" && next.style.display !== "none") { anyVisible = true; break; }
            next = next.nextElementSibling;
          }
          g.style.display = (!q || anyVisible) ? "" : "none";
        });
      });
    }
  } catch (e) {}

  // 3. Command palette (Ctrl+K) — quick jump, no page reload needed to find menu
  var PAGES = [
    ["Dashboard", "Overview, KPIs, recent", "/panel/"],
    ["All Purchases", "Market entries list", "/panel/market/"],
    ["Add Purchase", "New entry with bill", "/panel/market/add/"],
    ["All Items", "Bazaar item master", "/panel/items/"],
    ["Add Item", "New item + unit", "/panel/items/add/"],
    ["Bulk Add", "Many items at once", "/panel/items/bulk-add/"],
    ["Monthly Report", "Totals + export", "/panel/reports/monthly/"],
    ["Daily Report", "Day-wise detail", "/panel/reports/daily/"],
    ["Item-wise Report", "Per-item spend", "/panel/reports/item-wise/"],
    ["Export Center", "CSV / XLSX / PDF", "/panel/reports/export/"],
    ["Bill Manager", "Receipts + uploads", "/panel/uploads/bills/"],
    ["Activity Log", "Who did what", "/panel/activity/"],
    ["Profile", "Name, email", "/accounts/profile/"],
    ["Change Password", "Update login", "/accounts/password/"],
    ["Public Site", "See visitor view", "/"],
  ];
  var backdrop = document.getElementById("cmdkBackdrop");
  var input = document.getElementById("cmdkInput");
  var list = document.getElementById("cmdkList");
  function renderCmdk(q) {
    if (!list) return;
    q = (q || "").toLowerCase();
    var hits = PAGES.filter(function (p) {
      return !q || p[0].toLowerCase().indexOf(q) !== -1 || p[1].toLowerCase().indexOf(q) !== -1;
    }).slice(0, 9);
    list.innerHTML = "";
    hits.forEach(function (p, i) {
      var a = document.createElement("a");
      a.href = p[2];
      if (i === 0) a.className = "sel";
      a.innerHTML = "<span>→</span><span>" + p[0] + " <span class='muted'>— " + p[1] + "</span></span>";
      a.addEventListener("click", function () { closeCmdk(); });
      list.appendChild(a);
    });
    if (!hits.length) list.innerHTML = "<div class='muted' style='padding:12px'>Kuch nahi mila.</div>";
  }
  function openCmdk() {
    if (!backdrop || !input) return;
    backdrop.hidden = false;
    input.value = "";
    renderCmdk("");
    setTimeout(function () { input.focus(); }, 30);
  }
  function closeCmdk() { if (backdrop) backdrop.hidden = true; }
  try {
    var btn = document.getElementById("cmdkBtn");
    if (btn) btn.addEventListener("click", openCmdk);
    if (backdrop) backdrop.addEventListener("click", function (e) {
      if (e.target === backdrop) closeCmdk();
    });
    if (input) {
      input.addEventListener("input", function () { renderCmdk(input.value); });
      input.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          var first = list.querySelector("a");
          if (first) window.location.href = first.href;
        }
      });
    }
    document.addEventListener("keydown", function (e) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        if (backdrop.hidden) openCmdk(); else closeCmdk();
      }
    });
  } catch (e) {}

  // 4. KPI count-up (respects reduced motion)
  try {
    if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      document.querySelectorAll(".kpi strong[id]").forEach(function (node) {
        var raw = node.textContent.trim();
        var num = parseFloat(raw.replace(/[^0-9.]/g, ""));
        if (isNaN(num)) return;
        var prefix = raw.indexOf("₹") !== -1 ? "₹" : "";
        var t0 = null, dur = 650;
        function step(t) {
          if (!t0) t0 = t;
          var p = Math.min(1, (t - t0) / dur);
          var v = num * (1 - Math.pow(1 - p, 3));
          node.textContent = prefix + (Number.isInteger(num)
            ? Math.round(v).toLocaleString("en-IN")
            : v.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
          if (p < 1) requestAnimationFrame(step); else node.textContent = raw;
        }
        requestAnimationFrame(step);
      });
    }
  } catch (e) {}
})();
