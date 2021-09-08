resize();
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
    let redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/';
    let grp = document.getElementById("id_grp");
    if (grp && grp.value)
        redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/?view=list&lst=' + grp.value;
    window.location.href = redirect_url;
}

function delItem(app_name) {
    if (!confirm('Are you sure?'))
        return;

    let item_id = window.location.pathname.match( /\d+/ )[0];
    let redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/';
    let grp = document.getElementById("id_grp");
    if (grp && grp.value)
        redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/?view=list&lst=' + grp.value;

    const api = '/api/tasks/' + item_id + '/role_delete/?format=json&role=' + app_name;
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

function UploadFile()
{
    document.getElementById('id_upload').click();
}

function FileSelected()
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