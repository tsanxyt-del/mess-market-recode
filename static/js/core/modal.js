/* ============================================================
   v1.5 modal — robust confirm dialog (ESC + backdrop + focus)
   FIX: always re-query DOM, always hide on cancel/confirm.
   ============================================================ */
window.Modal = (function(){
  function els(){
    return {
      back: document.getElementById("confirmModal"),
      title: document.getElementById("modalTitle"),
      text: document.getElementById("modalText"),
      yes: document.getElementById("modalConfirm"),
      no: document.querySelector('[data-modal-close]')
    };
  }
  function hide(){
    const {back, yes} = els();
    if(back) back.hidden = true;            // [hidden] + CSS !important => always hides
    if(yes) yes.onclick = null;
    document.removeEventListener("keydown", onKey);
  }
  function onKey(e){ if(e.key === "Escape") hide(); }
  function confirm(title, text, onYes, danger){
    const {back, title: t, text: x, yes, no} = els();
    if(!back || !yes){ if(window.confirm(text || title)) onYes(); return; }
    t.textContent = title || "Please confirm";
    x.textContent = text || "Are you sure?";
    yes.textContent = danger === false ? "Confirm" : (yes.dataset.label || "Delete");
    back.hidden = false;
    if(no) no.onclick = hide;
    back.onclick = function(e){ if(e.target === back) hide(); };
    yes.onclick = function(){ hide(); onYes(); };
    document.addEventListener("keydown", onKey);
    setTimeout(function(){ try{ yes.focus(); }catch(_){} }, 30);
  }
  return { confirm: confirm, close: hide };
})();
