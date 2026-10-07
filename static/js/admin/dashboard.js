/* v1.5 admin/dashboard.js — refresh KPI band via API (progressive) */
document.addEventListener("DOMContentLoaded", function(){
  var els = {
    today: document.getElementById("kpiToday"),
    month: document.getElementById("kpiMonth"),
    days: document.getElementById("kpiDays")
  };
  if(!els.today && !els.month) return;
  window.API.get("/panel/api/stats/").then(function(data){
    if(!data || !data.ok || !data.stats) return;
    var s = data.stats;
    if(els.today) els.today.textContent = window.Utils.inr(s.today_total);
    if(els.month) els.month.textContent = window.Utils.inr(s.month_total);
    if(els.days) els.days.textContent = s.recorded_days;
  }).catch(function(){ /* server-rendered values stay */ });
});
