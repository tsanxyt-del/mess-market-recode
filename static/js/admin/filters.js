/* v1.5 admin/filters.js — AJAX table refresh + pagination hijack + skeleton */
document.addEventListener("DOMContentLoaded", function(){
  var form = document.getElementById("filterForm");
  var box = document.getElementById("recordsTable");
  var meta = document.getElementById("tableMeta");
  if(!form || !box) return;
  function skeleton(){
    box.innerHTML = '<div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div>';
  }
  function load(url){
    skeleton();
    fetch(url, {headers: {"X-Requested-With": "XMLHttpRequest"}})
      .then(function(r){ return r.json(); })
      .then(function(data){
        var box = document.getElementById("recordsTable");
        var pag = document.getElementById("paginationWrap");
        var meta = document.getElementById("tableMeta");
        if(data && data.ok){
          if(box) box.innerHTML = data.table || "";
          if(pag) pag.innerHTML = data.pagination || "";
          if(meta) meta.innerHTML = "<span>📄 Total <strong>" + data.total + "</strong> records • Page " + data.page + " of " + data.pages + "</span><span>₹" + data.page_sum + " is page ka kul</span>";
        }else if(box){
          box.innerHTML = (data && data.table) || "";
          if(pag && data) pag.innerHTML = data.pagination || "";
        }
        bindPagination();
        bindConfirms();
      })
      .catch(function(){
        box.innerHTML = '<div class="empty"><span class="empty-ico">⚠️</span><p>Failed to load. Please retry.</p></div>';
      });
  }
  function bindPagination(){
    var scope = document.getElementById("paginationWrap") || box;
    scope.querySelectorAll(".pagination a").forEach(function(a){
      a.addEventListener("click", function(e){
        e.preventDefault();
        var u = new URL(a.href, window.location.origin);
        window.history.replaceState(null, "", u.pathname + u.search);
        load(u.pathname + u.search);
      });
    });
  }
  function bindConfirms(){
    box.querySelectorAll('a[href$="/delete/"]').forEach(function(a){
      a.setAttribute("data-confirm", "Delete this purchase? It will be hidden from public totals (soft delete).");
    });
  }
  bindConfirms();
  var deb = window.Utils.debounce(function(){ form.requestSubmit(); }, 500);
  form.querySelectorAll('input[name="q"]').forEach(function(i){
    i.addEventListener("input", deb);
  });
  form.addEventListener("submit", function(e){
    e.preventDefault();
    var qs = new URLSearchParams(new FormData(form)).toString();
    var url = window.location.pathname + "?" + qs;
    window.history.replaceState(null, "", url);
    load(url);
  });
  form.querySelectorAll("select").forEach(function(s){
    s.addEventListener("change", function(){ form.requestSubmit(); });
  });
});
