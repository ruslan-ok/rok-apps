AddAutoResize();

function AddAutoResize()
{
  document.querySelectorAll('[data-autoresize]').forEach(function (element) {
  element.style.boxSizing = 'border-box';
  var offset = element.offsetHeight - element.clientHeight;
  element.style.minHeight = "25px";
  element.style.height = (element.scrollHeight + offset)+"px";
  element.addEventListener('input', function (event) {
    event.target.style.height = 'auto';
    event.target.style.height = event.target.scrollHeight + offset + 'px';});
  element.removeAttribute('data-autoresize');});
}
