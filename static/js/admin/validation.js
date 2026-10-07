/* v1.5 admin/validation.js — purchase form guards (backend re-validates all) */
document.addEventListener("DOMContentLoaded", function(){
  var form = document.getElementById("purchaseForm");
  if(!form) return;
  function mark(el, bad){
    if(!el) return;
    el.classList.toggle("field-err", !!bad);
  }
  form.addEventListener("submit", function(e){
    var d = document.getElementById("id_purchase_date");
    var n = document.getElementById("id_item_name");
    var q = document.getElementById("id_quantity");
    var r = document.getElementById("id_rate");
    var qv = parseFloat((q || {}).value || 0);
    var rv = parseFloat((r || {}).value || 0);
    var ok = true;
    if(!d || !d.value){ window.Toast.error("Purchase date is required."); mark(d, true); ok = false; }
    else mark(d, false);
    if(!n || !n.value.trim()){ window.Toast.error("Item is required — pick from the list."); mark(n, true); ok = false; }
    else mark(n, false);
    if(!(qv > 0)){ window.Toast.error("Quantity must be greater than 0."); mark(q, true); ok = false; }
    else mark(q, false);
    if(!(rv >= 0)){ window.Toast.error("Rate cannot be negative."); mark(r, true); ok = false; }
    else mark(r, false);
    if(qv > 100000){ window.Toast.error("Quantity looks unrealistically large."); mark(q, true); ok = false; }
    if(!ok) e.preventDefault();
    else{
      var btn = form.querySelector('button[type="submit"]');
      if(btn){ btn.disabled = true; btn.textContent = "Saving…"; }
    }
  });
});
