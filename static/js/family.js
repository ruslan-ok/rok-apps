function runAPI(api, callback, method='GET') {
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

function delItem() {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    let url_params = '';
    if (window.location.href.split('?').length == 2)
        url_params = '?' + window.location.href.split('?')[1];
    let redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/' + url_params;
    const api = '/api/famtree/' + item_id + '/?format=json&role=';
    const callback = function() {
        if (this.readyState == 4 && this.status == 204)
            window.location.href = redirect_url;
        if (this.readyState == 2 && this.status != 200) {            
            let info = `${this.status} ${this.statusText}`;
            iziToast.warning({message: info, position: 'bottomRight'});
        }
    };
    runAPI(api, callback, method='DELETE');
}

function updateMedia() {
    iziToast.warning({message: 'The feature has not yet been implemented.', position: 'bottomRight'});
}

function merge() {
    iziToast.warning({message: 'The feature has not yet been implemented.', position: 'bottomRight'});
}

function clone() {
    iziToast.warning({message: 'The feature has not yet been implemented.', position: 'bottomRight'});
}