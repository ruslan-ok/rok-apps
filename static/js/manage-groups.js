const group_api = '/ru/api/groups/';
const postfix = 'format=json';

tuneOnEnter();

function tuneOnEnter() {
  let input = document.getElementById('new_group_id');
  if (!input)
    return;
  input.addEventListener('keyup', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      document.getElementById('add_group_btn_id').click();
    }
  });
}

function addGroup(app, role) {
    let x = document.getElementById('new_group_id');
    if (!x)
      return;
    let name = x.value;
    if (!name)
      return;
  
    x.value = '';
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
  
    let url = window.location.protocol + '//' + window.location.host + group_api + '?' + postfix;
    let xhttp = new XMLHttpRequest();
    xhttp.open('POST', url, true);
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');
    
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 201) {
        group_id = JSON.parse(this.responseText).id;
        group_name = JSON.parse(this.responseText).name;
        group_url = `${window.location.protocol}//${window.location.host}/${app}/?view=by_group&group_id=${group_id}`;
        window.location.href = group_url;
      }
    };
  
    let data = {
      'app': app,
      'role': role,
      'node': null,
      'name': encodeURI(name),
      'sort': ''
    };

    xhttp.send(JSON.stringify(data));
}

function closeGroupForm() {
  let redirect_url = window.location.href.split('/group/')[0] + '/';
  const urlParams = new URLSearchParams(window.location.search);
  const group_id = urlParams.get('ret');
  if (group_id)
    redirect_url += '?view=by_group&group_id=' + group_id;
  window.location.href = redirect_url;
}

function showInfo(text) {
  let el = document.getElementById('infoModal');
  el.querySelectorAll('div.modal-body')[0].innerText = text;

  let message = new bootstrap.Modal(document.getElementById('infoModal'), {});
  message.show();
}

function delGroupConfirm(ban, text) {
  if (ban) {
    showInfo(ban);
    return;
  }

  let el = document.getElementById('delModal');
  el.querySelectorAll('div.modal-body')[0].innerText = text;
  el.querySelectorAll('button.btn-danger')[0].onclick = function() {return delGroup();}

  let conf = new bootstrap.Modal(document.getElementById('delModal'), {});
  conf.show();
}

function delGroup() {
  let id = window.location.pathname.match( /\d+/ )[0];
  let url = window.location.protocol + '//' + window.location.host + group_api + id + '/?' + postfix;
  let redirect_url = window.location.href.split('/group/')[0] + '/';
  let xhttp = new XMLHttpRequest();
  xhttp.open('DELETE', url, true);
  let y = document.getElementsByName('csrfmiddlewaretoken');
  let crsf = y[0].value; 
  xhttp.setRequestHeader('X-CSRFToken', crsf);
  xhttp.setRequestHeader('Content-type', 'application/json');
  
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 204) {
      window.location.href = redirect_url;
    }
  };

  xhttp.send();
}
