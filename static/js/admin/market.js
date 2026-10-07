/* v1.5 admin/market.js — live total + item sync + delete confirm + row highlight */
function calcTotal(){
  var q = parseFloat((document.getElementById("id_quantity") || {}).value || 0);
  var r = parseFloat((document.getElementById("id_rate") || {}).value || 0);
  var el = document.getElementById("liveTotal");
  if(el) el.textContent = window.Utils.inr(q * r);
  var hid = document.getElementById("calcTotalHidden");
  if(hid) hid.value = (Math.round(q * r * 100) / 100).toFixed(2);
}
/* v4.2: last-rate autofill — item chunte hi pichhli khareed ka rate (rate khaali ho tabhi) */
function autoFillRate(name){
  var rateEl = document.getElementById("id_rate");
  if(!rateEl || (rateEl.value !== "" && parseFloat(rateEl.value) > 0)) return;
  if(!name || !name.trim()) return;
  window.API.get("/panel/market/api/item-last/?name=" + encodeURIComponent(name.trim()))
    .then(function(data){
      if(data && data.ok && data.last){
        rateEl.value = data.last.rate;
        if(window.calcTotal) window.calcTotal();
        else if(typeof calcTotal === "function") calcTotal();
        window.Toast.ok("Pichhli rate lagi: ₹" + data.last.rate + " (" + (data.last.purchase_date_display || "") + ")");
      }
    }).catch(function(){});
}
function syncItemMeta(){
  var nameEl = document.getElementById("id_item_name");
  var idEl = document.getElementById("id_item_id");
  var unitEl = document.getElementById("id_unit");
  if(!nameEl) return;
  var dl = document.getElementById("item-list");
  var opt = dl ? Array.prototype.find.call(dl.options, function(o){ return o.value === nameEl.value; }) : null;
  if(opt){
    if(idEl) idEl.value = opt.getAttribute("data-id") || "";
    var u = opt.getAttribute("data-unit");
    if(u && unitEl) unitEl.value = u;
    nameEl.classList.remove("field-err");
  } else if(idEl) idEl.value = "";
}
document.addEventListener("DOMContentLoaded", function(){
  ["id_quantity", "id_rate"].forEach(function(id){
    var el = document.getElementById(id);
    if(el) el.addEventListener("input", calcTotal);
  });
  calcTotal();
  var nameEl = document.getElementById("id_item_name");
  if(nameEl){
    nameEl.addEventListener("input", function(){ syncItemMeta(); refreshQuickCreate(); renderSuggest(nameEl.value); });
    nameEl.addEventListener("change", function(){
      syncItemMeta();
      refreshQuickCreate();
      renderSuggest("");
      autoFillRate(nameEl.value);
    });
    syncItemMeta();
    refreshQuickCreate();
  }
  // Save & Add Next ke baad: item par focus taaki turant agla samaan likho
  try{
    var saved = new URLSearchParams(window.location.search).get("saved");
    if(saved === "1"){
      var ni = document.getElementById("id_item_name");
      if(ni){ ni.value = ""; ni.focus(); }
      var ii = document.getElementById("id_item_id");
      if(ii) ii.value = "";
    }
  }catch(_){}
  // v5.1: one-tap repeat — recent chip dabate hi item + unit + last rate bharo
  var chips = document.getElementById("recentChips");
  if(chips){
    chips.addEventListener("click", function(e){
      var b = e.target.closest(".chip");
      if(!b) return;
      var nameEl = document.getElementById("id_item_name");
      var unitEl = document.getElementById("id_unit");
      var rateEl = document.getElementById("id_rate");
      if(nameEl) nameEl.value = b.getAttribute("data-name") || "";
      if(unitEl && b.getAttribute("data-unit")) unitEl.value = b.getAttribute("data-unit");
      if(rateEl && (!rateEl.value || parseFloat(rateEl.value) <= 0))
        rateEl.value = b.getAttribute("data-rate") || "";
      syncItemMeta();
      calcTotal();
      var sg = document.getElementById("hindiSuggest");
      if(sg){ sg.style.display = "none"; sg.innerHTML = ""; }
      var q = document.getElementById("id_quantity");
      if(q){ q.focus(); }
    });
  }
  // v5.1: inline master create — list me naam na ho to turant jodo, page change nahi
  var qcBox = document.getElementById("quickCreate");
  var qcBtn = document.getElementById("quickCreateBtn");
  var qcName = document.getElementById("quickCreateName");
  function refreshQuickCreate(){
    var nameEl = document.getElementById("id_item_name");
    if(!nameEl || !qcBox) return;
    var v = (nameEl.value || "").trim();
    if(!v){ qcBox.style.display = "none"; return; }
    var dl = document.getElementById("item-list");
    var found = dl ? Array.prototype.some.call(dl.options, function(o){ return o.value === v; }) : false;
    if(found){ qcBox.style.display = "none"; }
    else{
      qcBox.style.display = "";
      if(qcName) qcName.textContent = "‘" + v + "’";
    }
  }
  if(qcBtn){
    qcBtn.addEventListener("click", function(){
      var nameEl = document.getElementById("id_item_name");
      var unitEl = document.getElementById("id_unit");
      var v = ((nameEl || {}).value || "").trim();
      if(!v) return;
      qcBtn.disabled = true;
      window.API.post("/panel/items/api/admin/", {
        name: v, default_unit: (unitEl || {}).value || "KG", category: "Other"
      }).then(function(data){
        qcBtn.disabled = false;
        if(data && data.ok){
          var dl = document.getElementById("item-list");
          if(dl){
            var opt = document.createElement("option");
            opt.value = v;
            opt.setAttribute("data-id", data.id || "");
            opt.setAttribute("data-unit", (unitEl || {}).value || "KG");
            dl.appendChild(opt);
          }
          syncItemMeta();
          refreshQuickCreate();
          window.Toast.ok("Master me jud gaya: " + v);
        }else{
          window.Toast.error((data && data.error) || "Jud nahi paya — Items page se try karo.");
        }
      }).catch(function(){ qcBtn.disabled = false; });
    });
  }
  // v5.2: Hindi naam sujhav — "aloo" likho to Potato ka button dikhega
  var MASTER = null;
  try {
    var tag = document.getElementById("items-data");
    MASTER = tag ? JSON.parse(tag.textContent || "[]") : [];
  } catch (_) { MASTER = []; }
  var sugBox = document.getElementById("hindiSuggest");
  function renderSuggest(q) {
    if (!sugBox || !MASTER) return;
    q = (q || "").trim().toLowerCase();
    if (q.length < 2) { sugBox.style.display = "none"; sugBox.innerHTML = ""; return; }
    var dl = document.getElementById("item-list");
    var exact = dl ? Array.prototype.some.call(dl.options, function (o) { return o.value.toLowerCase() === q; }) : false;
    if (exact) { sugBox.style.display = "none"; sugBox.innerHTML = ""; return; }
    var hits = [];
    for (var i = 0; i < MASTER.length && hits.length < 6; i++) {
      var m = MASTER[i];
      var nm = String(m.name || "");
      var al = m.aliases || [];
      var hay = (nm + " " + al.join(" ")).toLowerCase();
      if (hay.indexOf(q) !== -1) hits.push(m);
    }
    if (!hits.length) { sugBox.style.display = "none"; sugBox.innerHTML = ""; return; }
    sugBox.innerHTML = "";
    hits.forEach(function (m) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "suggest-btn";
      b.setAttribute("data-name", m.name);
      b.setAttribute("data-unit", m.default_unit || "KG");
      b.textContent = "🧺 " + (m.display_hi || m.name);
      sugBox.appendChild(b);
    });
    sugBox.style.display = "";
  }
  if (sugBox) {
    sugBox.addEventListener("click", function (e) {
      var b = e.target.closest(".suggest-btn");
      if (!b) return;
      var nameEl = document.getElementById("id_item_name");
      var unitEl = document.getElementById("id_unit");
      var rateEl = document.getElementById("id_rate");
      if (nameEl) nameEl.value = b.getAttribute("data-name") || "";
      if (unitEl && b.getAttribute("data-unit")) unitEl.value = b.getAttribute("data-unit");
      syncItemMeta();
      refreshQuickCreate();
      renderSuggest("");
      autoFillRate(nameEl ? nameEl.value : "");
      var q = document.getElementById("id_quantity");
      if (q) q.focus();
    });
  }
  // Delete links -> modal confirm (progressive enhancement over delete page)
  document.querySelectorAll('a[href$="/delete/"]').forEach(function(a){
    if(a.hasAttribute("data-confirm")) return;
    a.setAttribute("data-confirm", "Delete this purchase? It will be hidden from public totals (soft delete).");
  });
  // Highlight row flash after redirect (?flash=<id>)
  try{
    var id = new URLSearchParams(window.location.search).get("flash");
    if(id){
      var row = document.querySelector('[data-row="' + id + '"]');
      if(row){ row.style.background = "#fef9c3"; row.scrollIntoView({block: "center"}); }
    }
  }catch(_){}
});
