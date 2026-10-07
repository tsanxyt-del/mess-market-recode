/* v1.5 admin/reports.js — day-bars from server data (no chart lib needed) */
document.addEventListener("DOMContentLoaded", function(){
  document.querySelectorAll("[data-bar]").forEach(function(el){
    var pct = Math.max(2, Math.min(100, parseFloat(el.getAttribute("data-bar") || 0)));
    var fill = el.querySelector("i");
    if(fill){
      fill.style.width = "0%";
      requestAnimationFrame(function(){
        fill.style.transition = "width .6s cubic-bezier(.4,0,.2,1)";
        fill.style.width = pct + "%";
      });
    }
  });
});
