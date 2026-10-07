/* v1.5 admin/items.js — live search filter on the items table */
document.addEventListener("DOMContentLoaded", function(){
  var input = document.getElementById("itemSearch");
  var tbody = document.getElementById("itemRows");
  if(!input || !tbody) return;
  var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr[data-name]"));
  input.addEventListener("input", window.Utils.debounce(function(){
    var q = input.value.trim().toLowerCase();
    var shown = 0;
    rows.forEach(function(tr){
      var name = (tr.getAttribute("data-name") || "").toLowerCase();
      var alias = (tr.getAttribute("data-alias") || "").toLowerCase();
      var hit = !q || name.indexOf(q) !== -1 || alias.indexOf(q) !== -1;
      tr.style.display = hit ? "" : "none";
      if(hit) shown++;
    });
    var empty = document.getElementById("itemEmpty");
    if(empty) empty.style.display = shown ? "none" : "";
  }, 200));
  // Disable/enable links -> confirm
  document.querySelectorAll(".item-toggle").forEach(function(a){
    a.setAttribute("data-confirm", "Change the status of this item?");
  });
});
