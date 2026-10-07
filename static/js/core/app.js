/* v1.5 app — global init: sidebar active link + data-confirm + year */
document.addEventListener("DOMContentLoaded", function(){
  // 1. Sidebar + mobile tabbar active state (longest-prefix match)
  var path = window.location.pathname;
  document.querySelectorAll(".sidebar nav a").forEach(function(a){
    var href = a.getAttribute("href");
    if(href && href !== "#" && path.indexOf(href) === 0 && href.length > 1){
      a.classList.add("active");
    }
  });
  document.querySelectorAll(".app-tabbar a").forEach(function(a){
    var href = a.getAttribute("href");
    if(href && (path === href || (href !== "/" && path.indexOf(href) === 0))){
      a.classList.add("active");
    }
  });

  // 2. Generic confirm (deletion links etc.)
  document.addEventListener("click", function(e){
    var t = e.target.closest("[data-confirm]");
    if(!t) return;
    e.preventDefault();
    var href = t.getAttribute("href");
    window.Modal.confirm("Please confirm",
      t.getAttribute("data-confirm") || "Are you sure?",
      function(){ if(href) window.location.href = href; });
  });

  // 3. Dismissible alerts (click to fade)
  document.querySelectorAll(".alert").forEach(function(a){
    a.style.cursor = "pointer";
    a.title = "Click to dismiss";
    a.addEventListener("click", function(){ a.remove(); });
  });

  // 4. Footer year
  document.querySelectorAll("[data-year]").forEach(function(el){
    el.textContent = new Date().getFullYear();
  });
});
