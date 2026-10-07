/* v5.0 bill viewer — HQ lightbox: zoom, prev/next, open original, download */
(function () {
  var viewer = document.getElementById("billViewer");
  if (!viewer) return;
  var img = document.getElementById("bvImg");
  var stage = document.getElementById("bvStage");
  var title = document.getElementById("bvTitle");
  var open = document.getElementById("bvOpen");
  var dl = document.getElementById("bvDownload");
  var count = document.getElementById("bvCount");
  var thumbs = Array.prototype.slice.call(document.querySelectorAll(".bill-thumb"));
  var idx = 0, zoom = 1;

  function apply() {
    img.style.transform = "scale(" + zoom + ")";
    count.textContent = thumbs.length > 1 ? (idx + 1) + " / " + thumbs.length : "";
  }
  function show(i) {
    if (!thumbs.length) return;
    idx = (i + thumbs.length) % thumbs.length;
    var t = thumbs[idx];
    var full = t.getAttribute("data-full");
    img.src = full;
    zoom = 1;
    stage.scrollTop = 0; stage.scrollLeft = 0;
    if (title) title.textContent = t.getAttribute("data-title") || "Bill";
    if (open) open.href = full;
    if (dl) dl.href = full;
    apply();
  }
  function openAt(i) {
    viewer.hidden = false;
    document.body.style.overflow = "hidden";
    show(i);
  }
  function close() {
    viewer.hidden = true;
    document.body.style.overflow = "";
    img.src = "";
  }
  thumbs.forEach(function (t, i) {
    t.addEventListener("click", function () { openAt(i); });
  });
  document.getElementById("bvClose").addEventListener("click", close);
  viewer.addEventListener("click", function (e) { if (e.target === viewer) close(); });
  document.getElementById("bvZoomIn").addEventListener("click", function () {
    zoom = Math.min(4, zoom + 0.5); apply();
  });
  document.getElementById("bvZoomOut").addEventListener("click", function () {
    zoom = Math.max(1, zoom - 0.5); apply();
  });
  document.getElementById("bvPrev").addEventListener("click", function () { show(idx - 1); });
  document.getElementById("bvNext").addEventListener("click", function () { show(idx + 1); });
  document.addEventListener("keydown", function (e) {
    if (viewer.hidden) return;
    if (e.key === "Escape") close();
    else if (e.key === "ArrowRight") show(idx + 1);
    else if (e.key === "ArrowLeft") show(idx - 1);
    else if (e.key === "+" || e.key === "=") { zoom = Math.min(4, zoom + 0.5); apply(); }
    else if (e.key === "-") { zoom = Math.max(1, zoom - 0.5); apply(); }
  });
  // Pinch-ish: wheel + ctrl zooms desktop trackpads
  stage.addEventListener("wheel", function (e) {
    if (!e.ctrlKey) return;
    e.preventDefault();
    zoom = Math.min(4, Math.max(1, zoom + (e.deltaY < 0 ? 0.25 : -0.25)));
    apply();
  }, { passive: false });
})();
