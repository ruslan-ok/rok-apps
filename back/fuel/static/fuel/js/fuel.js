afterCalendarChanged(1, 1);

function afterCalendarChanged(init, field, django_host_api) {
    getRateOnDate(init, 'id_event', 'id_price_unit', 'id_expen_rate_usd', django_host_api);
}

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

function addService(car_id) {
    const part = document.getElementById('id_new_part');
    const value = part.options[part.selectedIndex].value;
    if (!value) {
        showInfo('Select car part.');
        return;
    }
    let param_serv = '&part_id=' + value;
    let param_group = '&group_id=' + car_id;
    const api = '/api/tasks/add_item/?format=json&app=fuel&role=service' + param_serv + param_group;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            let resp = JSON.parse(this.responseText);
            if (!resp || !resp.task_id) {
                let mess = 'Error';
                if (resp.mess)
                    mess += '\n' + resp.mess;
                iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
                return;
            }
            let item_id_arr = window.location.pathname.match( /\d+/ );
            let item_id = 0;
            if (item_id_arr && item_id_arr.length > 0)
                item_id = item_id_arr[0];
            let url_parts = window.location.href.split('?');
            let redirect_url = url_parts[0];
            if ((item_id != 0) && redirect_url.includes(item_id))
                redirect_url = redirect_url.replace(item_id, resp.task_id);
            else
                redirect_url = redirect_url + resp.task_id;
            if (url_parts.length > 1)
                redirect_url += '?' + url_parts[1];
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}