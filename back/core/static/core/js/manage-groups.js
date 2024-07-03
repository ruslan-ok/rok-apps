const group_api = '/api/groups/';
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

function getQueryVariable(variable) {
  var query = window.location.search.substring(1);
  var vars = query.split('&');
  for (var i = 0; i < vars.length; i++) {
      var pair = vars[i].split('=');
      if (decodeURIComponent(pair[0]) == variable) {
          return decodeURIComponent(pair[1]);
      }
  }
  console.log('Query variable %s not found', variable);
  return '';
}

function runGrpAPI(api, callback, method='GET') {
  const url = window.location.protocol + '//' + window.location.host + api;
  let xhttp = new XMLHttpRequest();
  xhttp.open(method, url, true);
  let y = document.getElementsByName('csrfmiddlewaretoken');
  let crsf = y[0].value; 
  xhttp.setRequestHeader('X-CSRFToken', crsf);
  xhttp.setRequestHeader('Content-type', 'application/json');
  xhttp.onreadystatechange = callback;
  xhttp.send();
}

function addGroup(app, role, group_entity) {
  let x = document.getElementById('new_group_id');
  if (!x)
    return;
  let name = x.value;
  if (!name)
    return;

  if (app == 'docs' || app == 'photo') {
    let cur_folder = getQueryVariable('folder');
    if (cur_folder.length > 0 && cur_folder[cur_folder.length-1] != '/')
      cur_folder += '/';
    const api = `${group_api}create_folder?${postfix}&app=${app}&folder=${cur_folder}&name=${name}`;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
          let res = 'error';
          let resp = JSON.parse(this.responseText);
          if (resp && resp.result)
              res = resp.result;
          if (res == 'ok') {
            console.log('The Folder created successfully.');
            const redirect_url = `${window.location.origin}${window.location.pathname}?folder=${cur_folder}${name}`;
            window.location.href = redirect_url;
          }
          else {
            let err = 'Unknown Error';
            if (res == 'error')
              err = resp.error;
            if (res == 'exception')
              err = resp.exception;
            console.log(err);
            let err_el = document.getElementById('id_add_group_error');
            err_el.innerText = err;
            err_el.classList.remove('d-none');
          }
        }
    };
    runGrpAPI(api, callback);
  }
  else {
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
        group_url = `${window.location.protocol}//${window.location.host}/${app}?${group_entity}=${group_id}`;
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

function editFolder(app, path, folder) {
  let el_view = document.getElementById('id_folder_view');
  let el_edit = document.getElementById('id_folder_edit');
  el_view.classList.add('d-none');
  el_edit.classList.remove('d-none');
  el_edit.childNodes[0].value = el_view.innerText;
  document.getElementById('id_folder_edit_btn').classList.add('d-none');
  document.getElementById('id_folder_del_btn').classList.add('d-none');
  document.getElementById('id_folder_save_btn').classList.remove('d-none');
  let err_el = document.getElementById('id_edit_folder_error');
  err_el.innerText = '';
}

function delFolderConfirm(app, path, folder, ban, text) {
  if (ban) {
    showInfo(ban);
    return;
  }

  let el = document.getElementById('delModal');
  el.querySelectorAll('div.modal-body')[0].innerText = text + ' ' + folder + '?';
  el.querySelectorAll('button.btn-danger')[0].onclick = function() {return delFolder(app, path, folder);}

  let conf = new bootstrap.Modal(document.getElementById('delModal'), {});
  conf.show();
}

function delFolder(app, path, folder) {
  const redirect_url = window.location.origin + window.location.pathname + `?folder=${path}`;
  const api = `${group_api}delete_folder?${postfix}&app=${app}&path=${path}&folder=${folder}`;
  const callback = function() {
    if (this.readyState == 4 && this.status == 200) {
      let res = 'error';
      let resp = JSON.parse(this.responseText);
      if (resp && resp.result)
          res = resp.result;
      if (res == 'ok') {
        console.log('The Folder deleted successfully.');
        window.location.href = redirect_url;
      }
      else {
        let err = 'Unknown Error';
        if (res == 'error')
          err = resp.error;
        if (res == 'exception')
          err = resp.exception;
        console.log(err);
        let err_el = document.getElementById('id_edit_folder_error');
        err_el.innerText = err;
        err_el.classList.remove('d-none');
      }
    }
  };
  runGrpAPI(api, callback);
}

function saveFolder(app, path, folder) {
  let el_view = document.getElementById('id_folder_view');
  let el_edit = document.getElementById('id_folder_edit');
  const new_name = el_edit.childNodes[0].value;

  if (folder == new_name) {
    el_view.classList.remove('d-none');
    el_edit.classList.add('d-none');
    document.getElementById('id_folder_edit_btn').classList.remove('d-none');
    document.getElementById('id_folder_del_btn').classList.remove('d-none');
    document.getElementById('id_folder_save_btn').classList.add('d-none');
    let err_el = document.getElementById('id_edit_folder_error');
    err_el.innerText = '';
    return;
  }
  
  const redirect_url = window.location.origin + window.location.pathname + `?folder=${path}${new_name}`;
  const api = `${group_api}rename_folder?${postfix}&app=${app}&path=${path}&folder=${folder}&new_name=${new_name}`;
  const callback = function() {
    if (this.readyState == 4 && this.status == 200) {
      let res = 'error';
      let resp = JSON.parse(this.responseText);
      if (resp && resp.result)
          res = resp.result;
      if (res == 'ok') {
        console.log('The Folder renamed successfully.');
        window.location.href = redirect_url;
      }
      else {
        let err = 'Unknown Error';
        if (res == 'error')
          err = resp.error;
        if (res == 'exception')
          err = resp.exception;
        console.log(err);
        let err_el = document.getElementById('id_edit_folder_error');
        err_el.innerText = err;
        err_el.classList.remove('d-none');
      }
    }
  };
  runGrpAPI(api, callback);
}
