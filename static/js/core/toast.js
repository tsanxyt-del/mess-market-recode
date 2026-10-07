/* v1.5 toast — styled via global.css (.toast classes) */
window.Toast = {
  show(msg, type){
    let box = document.getElementById("toastBox");
    if(!box){
      box = document.createElement("div");
      box.id = "toastBox";
      document.body.appendChild(box);
    }
    const el = document.createElement("div");
    el.className = "toast" + (type === "error" ? " toast-error" : type === "ok" ? " toast-ok" : "");
    el.textContent = msg;
    box.appendChild(el);
    setTimeout(function(){ el.style.opacity = "0"; el.style.transition = "opacity .3s"; }, 3200);
    setTimeout(function(){ el.remove(); }, 3600);
    while(box.children.length > 4) box.firstChild.remove();
  },
  ok(msg){ this.show(msg, "ok"); },
  error(msg){ this.show(msg, "error"); }
};
