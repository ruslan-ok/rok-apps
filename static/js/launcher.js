function launcherOpen() {
  let el = document.getElementById("launcher");
  el.classList.remove('d-none');
}

function launcherClose() {
  let el = document.getElementById("launcher");
  el.classList.add('d-none');
}

function asideToggle() {
  document.getElementById("aside").style.display = "flex";
}

function asideClose() {
  document.getElementById("aside").style.display = "none";
}
    
let element = document.getElementById("autofocus");
if (element)
  element.focus();
