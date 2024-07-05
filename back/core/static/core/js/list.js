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

function toggleSubGroup(div, group_id, sub_group_id) {
    const hidden = document.getElementById('id-sub-group-' + sub_group_id).classList.toggle('d-none');
    if (hidden) {
        div.children[0].classList.remove('bi-chevron-down');
        div.children[0].classList.add('bi-chevron-right');
    } else {
        div.children[0].classList.remove('bi-chevron-right');
        div.children[0].classList.add('bi-chevron-down');
    }
    const api = '/api/groups/' + group_id + '/toggle_sub_group/?format=json&sub_group_id=' + sub_group_id;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Sub group ' + sub_group_id + ' toggled successfully.');
        }
    };
    runAPI(api, callback);
}

function setTheme(group_id, theme_id) {
    const redirect_url = window.location.href;
    const api = '/api/groups/' + group_id + '/set_theme/?format=json&theme_id=' + theme_id;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Theme ' + theme_id + ' setted successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function setSort(group_id, sort_id) {
    const redirect_url = window.location.href;
    const api = '/api/groups/' + group_id + '/set_sort/?format=json&sort_id=' + sort_id;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Sort ' + sort_id + ' setted successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function reverseSort(group_id) {
    const redirect_url = window.location.href;
    const api = '/api/groups/' + group_id + '/reverse_sort/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Sort reversed successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function delSort(group_id) {
    const redirect_url = window.location.href;
    const api = '/api/groups/' + group_id + '/delete_sort/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Sort deleted successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function toggleSubGroups(group_id) {
    const redirect_url = window.location.href;
    const api = '/api/groups/' + group_id + '/toggle_sub_groups/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Using sub groups changed successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function toggleServicesVisible(group_id) {
    const redirect_url = window.location.href;
    const api = '/api/groups/' + group_id + '/toggle_services_visible/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Showing service tasks changed successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function toggleCompleted(item_id) {
    const redirect_url = window.location.href;
    const api = '/api/tasks/' + item_id + '/completed/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            let info = '';
            if (this.response) {
                let resp = JSON.parse(this.response);
                if (resp && resp.info)
                    info = resp.info;
            }
            if (info == '')
                window.location.href = redirect_url;
            else {
                iziToast.info({message: info, position: 'bottomRight'});
                setTimeout(function(){window.location.href = redirect_url;}, 1000);
            }
        }
    };
    runAPI(api, callback);
}

function toggleImportant(item_id, api_role='tasks', redirect=true) {
    if (!api_role)
        api_role = 'tasks';
    const redirect_url = window.location.href;
    let method = 'important';
    if (api_role == 'famtree')
        method = 'set_active';
    const api = `/api/${api_role}/${item_id}/${method}/?format=json`;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            if (redirect)
                window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function addItem(app, role, group_id, screen_size='') {
    let param_name = '';
    let id = 'id_add_item_name';
    if (screen_size != '')
        id += '_' + screen_size;
    var name = document.getElementById(id);
    if (name)
        param_name = '&name=' + name.value;
    param_group = '&group_id=' + group_id;
    const api = '/api/tasks/add_item/?format=json&app=' + app + '&role=' + role + param_name + param_group;
    const callback = function() {
        if (this.readyState == 4 && this.status == 400) {
            if (this.response) {
                console.log(this.response);
                let mess = 'Unknown error'
                let resp = JSON.parse(this.response);
                if (resp && resp.Error)
                    mess = resp.Error;
                iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
            }
        }
        if (this.readyState == 4 && this.status == 200) {
            let resp = JSON.parse(this.responseText);
            if (!resp || !resp.task_id) {
                let mess = 'Unknown Error';
                if (resp.mess)
                    mess = resp.mess;
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
            else {
                if (!redirect_url.endsWith('/'))
                    redirect_url += '/';
                redirect_url = redirect_url + resp.task_id;
            }
            if (url_parts.length > 1)
                redirect_url += '?' + url_parts[1];
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

