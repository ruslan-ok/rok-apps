function launcherOpen() {
  document.getElementById("launcher").style.display = "flex";
}

function launcherClose() {
  document.getElementById("launcher").style.display = "none";
}

var element = document.getElementById("autofocus");
if (element)
  element.focus();
