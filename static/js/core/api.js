/* v1.5 api — fetch wrapper with ok/error normalization + timeout */
window.API = (function(){
  function headers(json){
    var h = {"X-Requested-With": "XMLHttpRequest"};
    try{ h["X-CSRFToken"] = window.CSRF.get(); }catch(_){}
    if(json) h["Content-Type"] = "application/json";
    return h;
  }
  function check(r){
    if(r.status === 401){ window.Toast.error("Session expired — please login again."); }
    if(r.status === 403){ window.Toast.error("Security token expired — page reload karo."); }
    if(r.redirected || r.status === 302){ window.Toast.error("Session expired — please login again."); }
    return r.text().then(function(t){
      try{ return JSON.parse(t); }
      catch(_){ return {ok: false, error: "Bad response (" + r.status + ")"}; }
    });
  }
  return {
    get(url){ return fetch(url, {headers: headers(false)}).then(check); },
    post(url, data){
      return fetch(url, {method: "POST", headers: headers(true),
        body: JSON.stringify(data || {})}).then(check);
    },
    postForm(url, formData){
      return fetch(url, {method: "POST", headers: headers(false), body: formData}).then(check);
    }
  };
})();
