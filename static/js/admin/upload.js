/* v1.5 admin/upload.js — client checks + file chip preview */
document.addEventListener("DOMContentLoaded", function(){
  var input = document.querySelector('input[type="file"]');
  if(!input) return;
  var chip = document.getElementById("fileChip");
  input.addEventListener("change", function(){
    var f = input.files[0];
    if(!f){ if(chip) chip.style.display = "none"; return; }
    var ok = ["jpg", "jpeg", "png", "webp", "pdf"];
    var ext = (f.name.split(".").pop() || "").toLowerCase();
    if(ok.indexOf(ext) === -1){
      window.Toast.error("Invalid file type. Allowed: JPG, PNG, WEBP, PDF.");
      input.value = "";
      if(chip) chip.style.display = "none";
      return;
    }
    if(f.size > 5 * 1024 * 1024){
      window.Toast.error("File too large. Max 5 MB.");
      input.value = "";
      if(chip) chip.style.display = "none";
      return;
    }
    if(chip){
      chip.style.display = "";
      chip.textContent = "📎 " + f.name + " (" + (f.size / 1024).toFixed(0) + " KB)";
    } else {
      window.Toast.ok("File ready: " + f.name);
    }
  });
});
