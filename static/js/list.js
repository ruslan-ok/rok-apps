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
