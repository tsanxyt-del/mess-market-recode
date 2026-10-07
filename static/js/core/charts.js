/* v4.2 charts — dependency-free canvas bar chart (no Chart.js needed).
   Auto-inits: <canvas id="spendChart"> + JSON from #chart-data ([{label, amount}]).
   Works in light + dark mode, HiDPI sharp, responsive redraw. */
window.Charts = (function(){
  var PALETTE = ["#16a34a", "#2563eb", "#d97706", "#dc2626", "#7c3aed", "#0ea5e9"];
  function shortLabel(r){
    var s = String(r.label || r.date || r.display || "");
    var m = s.match(/(\d{4})-(\d{2})-(\d{2})/);
    if(m) return m[3];  // "2026-10-01" -> "01"
    return s.slice(0, 8);
  }
  function css(v, fb){
    try{
      var val = getComputedStyle(document.documentElement).getPropertyValue(v);
      return (val && val.trim()) || fb;
    }catch(_){ return fb; }
  }
  function draw(canvas, rows){
    if(!canvas || !canvas.getContext) return;
    var dpr = window.devicePixelRatio || 1;
    var W = canvas.clientWidth || canvas.parentElement.clientWidth || 600;
    var H = parseInt(canvas.getAttribute("height") || "240", 10);
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    var ctx = canvas.getContext("2d");
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, W, H);
    var dark = document.documentElement.getAttribute("data-theme") === "dark";
    var grid = dark ? "#26314f" : "#e3e8f0";
    var txt = dark ? "#b9c4e2" : "#6b7280";
    var padL = 52, padB = 30, padT = 22, padR = 8;
    if(!rows || !rows.length){
      ctx.fillStyle = txt;
      ctx.font = "14px system-ui";
      ctx.textAlign = "center";
      ctx.fillText("📭 Is period me koi record nahi", W / 2, H / 2);
      return;
    }
    var max = Math.max.apply(null, rows.map(function(r){ return Number(r.amount) || 0; }).concat([1]));
    // gridlines (4)
    ctx.strokeStyle = grid;
    ctx.fillStyle = txt;
    ctx.font = "11px system-ui";
    ctx.textAlign = "right";
    for(var g = 0; g <= 4; g++){
      var y = padT + (H - padT - padB) * g / 4;
      ctx.beginPath();
      ctx.moveTo(padL, y);
      ctx.lineTo(W - padR, y);
      ctx.stroke();
      ctx.fillText("₹" + Math.round(max * (4 - g) / 4).toLocaleString("en-IN"), padL - 6, y + 4);
    }
    // bars
    var n = rows.length;
    var slot = (W - padL - padR) / n;
    var bw = Math.max(10, Math.min(54, slot * 0.58));
    rows.forEach(function(r, i){
      var v = Number(r.amount) || 0;
      var h = Math.max(3, (H - padT - padB) * v / max);
      var x = padL + slot * i + (slot - bw) / 2;
      var y = H - padB - h;
      var grad = ctx.createLinearGradient(0, y, 0, y + h);
      var base = PALETTE[i % PALETTE.length];
      grad.addColorStop(0, base);
      grad.addColorStop(1, base + "88");
      ctx.fillStyle = grad;
      ctx.beginPath();
      if(ctx.roundRect) ctx.roundRect(x, y, bw, h, [6, 6, 0, 0]);
      else ctx.rect(x, y, bw, h);
      ctx.fill();
      // value on top
      ctx.fillStyle = dark ? "#e8edf7" : "#141a26";
      ctx.font = "bold 11px system-ui";
      ctx.textAlign = "center";
      ctx.fillText("₹" + Math.round(v).toLocaleString("en-IN"), x + bw / 2, y - 6);
      // x label
      ctx.fillStyle = txt;
      ctx.font = "10px system-ui";
      ctx.fillText(shortLabel(r), x + bw / 2, H - padB + 14);
    });
  }
  function auto(){
    var c = document.getElementById("spendChart");
    var tag = document.getElementById("chart-data");
    if(!c || !tag) return;
    var rows = [];
    try{ rows = JSON.parse(tag.textContent || "[]"); }
    catch(_){ rows = []; }
    function render(){ draw(c, rows); }
    render();
    var t;
    window.addEventListener("resize", function(){
      clearTimeout(t);
      t = setTimeout(render, 150);
    });
    // redraw after theme toggle (colors adapt)
    document.addEventListener("click", function(e){
      if(e.target.closest("[data-theme-toggle]")) setTimeout(render, 60);
    });
  }
  document.addEventListener("DOMContentLoaded", auto);
  return { drawBars: draw, auto: auto };
})();
