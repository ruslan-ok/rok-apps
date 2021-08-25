function navPanelOpen(id) {
  let el = document.getElementById(id);
  if (el)
  el.classList.toggle('d-none');
}

function navPanelClose(id) {
  let el = document.getElementById(id);
  if (el)
  el.classList.add('d-none');
}

let element = document.getElementById("autofocus");
if (element)
  element.focus();
