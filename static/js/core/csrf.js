/* csrf: read csrftoken cookie (set by Django CsrfViewMiddleware) */
window.CSRF = {
  get(){
    const m=document.cookie.match(/csrftoken=([^;]+)/);
    return m?decodeURIComponent(m[1]):"";
  }
};
