function linkClick(event) {
  event.preventDefault();
  var url = this.href;
  window.location.href = url;
}

const menus = document.querySelectorAll('.immediate-link');
for (let i = 0; i < menus.length; i++)
  menus[i].addEventListener('click', linkClick);
