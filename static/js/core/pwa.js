/* v5.0 PWA — register service worker, standalone class, install prompt.
   Install button rule: jis phone me app install ho jaye, usme button kabhi na dikhe
   (standalone + appinstalled event + localStorage flag, teeno se pakka). */
(function(){
  var FLAG = "mmm-installed";
  function standalone(){
    try{
      return window.matchMedia("(display-mode: standalone)").matches ||
             window.navigator.standalone === true;
    }catch(_){ return false; }
  }
  function remembered(){
    try{ return localStorage.getItem(FLAG) === "1"; }catch(_){ return false; }
  }
  function markInstalled(){
    try{ localStorage.setItem(FLAG, "1"); }catch(_){}
    document.documentElement.classList.add("is-installed");
    hideInstall();
  }
  function isInstalled(){ return standalone() || remembered(); }
  function hideInstall(){
    document.querySelectorAll("[data-install-app], [data-install-promo]").forEach(function(b){
      b.style.display = "none";
    });
  }
  // 1. Service worker (same-origin only, fails silently offline-first-run)
  if("serviceWorker" in navigator){
    window.addEventListener("load", function(){
      navigator.serviceWorker.register("/sw.js").catch(function(){});
    });
  }
  // 2. App-mode + installed class
  function mark(){
    var solo = standalone();
    document.documentElement.classList.toggle("app-mode", solo);
    if(isInstalled()){
      document.documentElement.classList.add("is-installed");
      hideInstall();
    }
    try{
      var mq = window.matchMedia("(display-mode: standalone)");
      if(mq.addEventListener) mq.addEventListener("change", mark);
      else if(mq.addListener) mq.addListener(mark);
    }catch(_){}
  }
  document.addEventListener("DOMContentLoaded", mark);
  mark();
  // 2b. Offline indicator bar (PWA cache serves old pages offline)
  function netBar(){
    var bar = document.getElementById("offlineBar");
    if(!bar) return;
    function upd(){ bar.hidden = navigator.onLine; }
    window.addEventListener("online", upd);
    window.addEventListener("offline", upd);
    upd();
  }
  document.addEventListener("DOMContentLoaded", netBar);
  // 3. Install button — sirf tab dikhao jab app installed NA ho
  var pending = null;
  window.addEventListener("beforeinstallprompt", function(e){
    if(isInstalled()) return;
    e.preventDefault();
    pending = e;
    document.querySelectorAll("[data-install-app]").forEach(function(b){
      b.style.display = "";
    });
    document.querySelectorAll("[data-install-promo]").forEach(function(b){
      b.style.display = "";
    });
  });
  window.addEventListener("appinstalled", function(){ markInstalled(); });
  document.addEventListener("click", function(e){
    var b = e.target.closest("[data-install-app]");
    if(!b || !pending || isInstalled()) return;
    pending.prompt();
    try{
      pending.userChoice.then(function(choice){
        pending = null;
        if(choice && choice.outcome === "accepted") markInstalled();
      }).catch(function(){});
    }catch(_){ pending = null; }
  });
})();
