//resize();
moveLists();

function resize()
{
    document.querySelectorAll('[data-autoresize]').forEach(function (element) {
        element.style.boxSizing = 'border-box';
        var offset = element.offsetHeight - element.clientHeight;
        element.style.minHeight = "25px";
        element.style.height = (element.scrollHeight + offset)+"px";
        element.addEventListener('input', function (event) {
            event.target.style.height = 'auto';
            event.target.style.height = event.target.scrollHeight+ offset + 'px';
        });
        element.removeAttribute('data-autoresize');
    });
}

function moveLists() {
    let el_src = document.getElementById('url-list-src');
    let el_dst = document.getElementById('url-list-dst');
    if (el_src && el_dst)
        el_dst.appendChild(el_src); 
    el_src = document.getElementById('file-list-src');
    el_dst = document.getElementById('file-list-dst');
    if (el_src && el_dst)
        [...el_src.children].forEach((chl) => el_dst.appendChild(chl))
}

function closeForm() {
    let item_id = window.location.pathname.match( /\d+/ )[0];
    let redirect_url = window.location.href.replace('/' + item_id + '/', '/');
    window.location.href = redirect_url;
}

function addItem(app, role) {
    const api = '/api/tasks/add_item/?format=json&app=' + app + '&role=' + role;
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            let resp = JSON.parse(this.responseText);
            if (!resp || !resp.task_id) {
                let mess = 'Error';
                if (resp.mess)
                    mess += '\n' + resp.mess;
                alert(mess);
                return;
            }
            let url_parts = window.location.href.split('?');
            let redirect_url = url_parts[0] + resp.task_id + '/';
            if (url_parts.length > 1)
                redirect_url += '?' + url_parts[1];
            window.location.href = redirect_url;
        }
    };

    xhttp.send();
}

function showInfo(text) {
    let el = document.getElementById('infoModal');
    el.querySelectorAll('div.modal-body')[0].innerText = text;

    let message = new bootstrap.Modal(document.getElementById('infoModal'), {});
    message.show();
}

function delItemConfirm(role, ban, text) {
    if (ban) {
        showInfo(ban);
        return;
      }
    
    let el = document.getElementById('delModal');
    el.querySelectorAll('div.modal-body')[0].innerText = text;
    el.querySelectorAll('button.btn-danger')[0].onclick = function() {return delItem(role);}

    let conf = new bootstrap.Modal(document.getElementById('delModal'), {});
    conf.show();
}

function delItem(role) {
    let item_id = window.location.pathname.match( /\d+/ )[0];
    let redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/';
    let grp = document.getElementById("id_grp");
    if (grp && grp.value)
        redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/?view=by_group&group_id=' + grp.value;

    const api = '/api/tasks/' + item_id + '/role_delete/?format=json&role=' + role;
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = redirect_url;
        }
    };

    xhttp.send();
}

function delCategory(category) {
    let item_id = window.location.pathname.match( /\d+/ )[0];
    let redirect_url = window.location.href;
    const api = '/api/tasks/' + item_id + '/category_delete/?format=json&category=' + category;
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = redirect_url;
        }
    };

    xhttp.send();
}

function delURL(url_id) {
    const api = '/api/urls/' + url_id + '/?format=json';
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('DELETE', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 204) {
            console.log('deleted URL');
        }
    };

    xhttp.send();

    let el = document.getElementById('id_url_' + url_id);
    if (el) {
        el.parentElement.removeChild(el);
    }
}

function uploadFile()
{
    document.getElementById('id_upload').click();
}

function fileSelected()
{
    filename = document.getElementById('id_upload').files[0].name;
    fn_element = document.getElementById('loadFile');
    if (fn_element)
        fn_element.innerText = filename;
    document.getElementById('id_submit').click();
}

function delFile(app, role, fname, file_id) {
    let item_id = window.location.pathname.match( /\d+/ )[0];
    const api = '/api/tasks/' + item_id + '/file_delete/?format=json&app=' + app + '&role=' + role + '&fname=' + fname;
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 204) {
            console.log('deleted file ' + fname);
        }
    };

    xhttp.send();

    let el = document.getElementById('id_file_' + file_id);
    if (el) {
        el.parentElement.removeChild(el);
    }
}

function getAvatar() {
    document.getElementById('id_avatar').click();
}

function avatarSelected()
{
    filename = document.getElementById('id_avatar').files[0].name;
    document.getElementById('id_submit').click();
}

function delAvatar() {
    let redirect_url = window.location.href;
    const api = '/api/profile/delete_avatar/?format=json';
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('deleted profile avatar');
            window.location.href = redirect_url;
        }
    };

    xhttp.send();
}

function toggleCompleted(item_id) {
    let redirect_url = window.location.href;
    const api = '/api/tasks/' + item_id + '/completed/?format=json';
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = redirect_url;
        }
    };

    xhttp.send();
}

function toggleImportant(item_id, redirect=true) {
    let redirect_url = window.location.href;
    const api = '/api/tasks/' + item_id + '/important/?format=json';
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            if (redirect)
                window.location.href = redirect_url;
        }
    };

    xhttp.send();
}


function toggleFormImportant() {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    let el = document.getElementById('toggle-important');
    let img = el.querySelectorAll('i')[0];
    let checked = el.hasAttribute('checked');
    if (checked) {
        el.removeAttribute('checked');
        img.classList.remove('bi-star-fill');
        img.classList.add('bi-star');
    }
    else {
        el.setAttribute('checked', '');
        img.classList.remove('bi-star');
        img.classList.add('bi-star-fill');
    }
    toggleImportant(item_id, false);
}

function apartChange(selectObject) {
    var value = selectObject.value;
    let redirect_url = window.location.href;
    const api = '/api/apart/' + value + '/set_active/?format=json';
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if ((this.readyState == 4 || this.readyState == 2)  && this.status == 200) {
            window.location.href = redirect_url;
        }
    };

    xhttp.send();
}

function addRole(role) {
    let redirect_url = window.location.href;
    let item_id = window.location.pathname.match( /\d+/ )[0];
    const api = '/api/tasks/' + item_id + '/role_add/?format=json&role=' + role;
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = redirect_url;
        }
    };

    xhttp.send();
}

function delRole(role) {
    let item_id = window.location.pathname.match( /\d+/ )[0];
    let redirect_url = window.location.href;
    const api = '/api/tasks/' + item_id + '/role_delete/?format=json&role=' + role;
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if ((this.readyState == 4 || this.readyState == 2)  && this.status == 200) {
            window.location.href = redirect_url;
        }
    };

    xhttp.send();
}

function ToggleSelectField(name)
{
  var sel_id = name + '-select';
  document.getElementById(sel_id).classList.toggle('d-none');
}

