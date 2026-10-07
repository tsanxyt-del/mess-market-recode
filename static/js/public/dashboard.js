/* public dashboard: auto-submit on selector change */
document.addEventListener("DOMContentLoaded",()=>{
  const f=document.getElementById("monthForm");
  if(!f) return;
  ["yearSel","monthSel"].forEach(id=>{
    const el=document.getElementById(id);
    if(el) el.addEventListener("change",()=>f.submit());
  });
});
