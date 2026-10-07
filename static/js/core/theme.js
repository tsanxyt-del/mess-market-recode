/* v2.0 theme — dark/light toggle persisted in localStorage (NOT the database) */
(function(){
  var KEY = "mmm-theme";
  function apply(t){
    document.documentElement.setAttribute("data-theme", t);
    document.querySelectorAll("[data-theme-toggle]").forEach(function(b){
      b.textContent = t === "dark" ? "☀️" : "🌙";
      b.setAttribute("aria-pressed", t === "dark" ? "true" : "false");
      b.setAttribute("aria-label", t === "dark" ? "Light mode karo" : "Dark mode karo");
      b.title = t === "dark" ? "Light mode" : "Dark mode";
    });
  }
  function current(){
    try{ return localStorage.getItem(KEY) || "light"; }
    catch(_){ return "light"; }
  }
  document.addEventListener("DOMContentLoaded", function(){
    apply(current());
    document.querySelectorAll("[data-theme-toggle]").forEach(function(b){
      b.addEventListener("click", function(){
        var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
        try{ localStorage.setItem(KEY, next); }catch(_){}
        apply(next);
      });
    });
  });
  apply(current());
})();
