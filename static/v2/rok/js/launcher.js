function launcher_open()
{
  document.getElementById("launcher").style.display = "flex";
}

function launcher_close()
{
  document.getElementById("launcher").style.display = "none";
}

var element = document.getElementById("autofocus");
if (element)
  element.focus();
