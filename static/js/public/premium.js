/* v5.0 premium UX: reveal-on-scroll + count-up + hidden shortcuts */
(function () {
  try {
    var els = document.querySelectorAll(".day-card, .hstat, .hero");
    els.forEach(function (el) { el.classList.add("reveal"); });
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
        });
      }, { threshold: 0.08 });
      els.forEach(function (el) { io.observe(el); });
    } else {
      els.forEach(function (el) { el.classList.add("in"); });
    }
  } catch (e) {}

  try {
    document.querySelectorAll(".hstat strong").forEach(function (node) {
      var raw = node.textContent.trim();
      var num = parseFloat(raw.replace(/[^0-9.]/g, ""));
      if (isNaN(num)) return;
      var prefix = raw.startsWith("₹") ? "₹" : "";
      var dur = 700, t0 = null;
      function step(t) {
        if (!t0) t0 = t;
        var p = Math.min(1, (t - t0) / dur);
        var v = num * (0.2 + 0.8 * p * (2 - p));
        node.textContent = prefix + (Number.isInteger(num) ? Math.round(v).toLocaleString("en-IN") : v.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
        if (p < 1) requestAnimationFrame(step);
        else node.textContent = raw;
      }
      if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches) requestAnimationFrame(step);
    });
  } catch (e) {}

  try {
    var ENTRY = atob("L2FjY291bnRzL2xvZ2luLw==");
    var brand = document.getElementById("brandHome");
    var clicks = 0, timer = null;
    if (brand) brand.addEventListener("click", function (ev) {
      clicks++;
      clearTimeout(timer);
      timer = setTimeout(function () { clicks = 0; }, 600);
      if (clicks >= 3) { ev.preventDefault(); clicks = 0; window.location.href = ENTRY; }
    });
    var dot = document.getElementById("footDot");
    var dotClicks = 0;
    if (dot) dot.addEventListener("click", function () {
      dotClicks++;
      if (dotClicks >= 5) { dotClicks = 0; window.location.href = ENTRY; }
      setTimeout(function () { dotClicks = 0; }, 1200);
    });
    var buf = "";
    document.addEventListener("keydown", function (ev) {
      if (ev.ctrlKey && ev.shiftKey && ev.key.toLowerCase() === "a") { window.location.href = ENTRY; return; }
      if (/^[a-z]$/i.test(ev.key)) {
        buf = (buf + ev.key.toLowerCase()).slice(-5);
        if (buf === atob("c3RhZmY=")) { buf = ""; window.location.href = ENTRY; }
      }
    });
  } catch (e) {}

  // Back-to-top floating button
  try {
    var toTop = document.getElementById("toTop");
    if (toTop) {
      window.addEventListener("scroll", function () {
        toTop.classList.toggle("show", window.scrollY > 600);
      }, { passive: true });
      toTop.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
      });
    }
  } catch (e) {}
})();
