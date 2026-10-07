/* v4.3 share — Web Share API (app feel) with WhatsApp fallback.
   Buttons: <button data-share data-share-text="...">Share</button> */
document.addEventListener("click", function(e){
  var b = e.target.closest("[data-share]");
  if(!b) return;
  var title = b.getAttribute("data-share-title") || document.title;
  var text = b.getAttribute("data-share-text") || "";
  var url = b.getAttribute("data-share-url") || window.location.href;
  if(navigator.share){
    navigator.share({title: title, text: text, url: url}).catch(function(){});
  }else{
    window.open("https://wa.me/?text=" + encodeURIComponent(text + " " + url), "_blank");
  }
});
