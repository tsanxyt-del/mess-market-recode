/* v1.5 utils — formatting, debounce, query helpers, download */
window.Utils = {
  inr(n){
    var v = Number(n || 0);
    return "₹" + v.toLocaleString("en-IN", {maximumFractionDigits: 2});
  },
  num(n, d){
    return Number(n || 0).toLocaleString("en-IN", {maximumFractionDigits: (d == null ? 2 : d)});
  },
  debounce(fn, ms){
    var t;
    return function(){
      var a = arguments, self = this;
      clearTimeout(t);
      t = setTimeout(function(){ fn.apply(self, a); }, ms || 300);
    };
  },
  qs(s, r){ return (r || document).querySelector(s); },
  qsa(s, r){ return Array.prototype.slice.call((r || document).querySelectorAll(s)); },
  fmtDate(iso){
    try{
      var d = new Date(iso + "T00:00:00");
      return d.toLocaleDateString("en-IN", {day: "2-digit", month: "long", year: "numeric"});
    }catch(_){ return iso; }
  }
};
