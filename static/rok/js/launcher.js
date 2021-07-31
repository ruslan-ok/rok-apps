function launcherOpen() {
  document.getElementById("launcher").style.display = "flex";
}

function launcherClose() {
  document.getElementById("launcher").style.display = "none";
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
