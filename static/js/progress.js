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

function checkResp(resp, params) {
    if (!resp)
        return 'Bad responce';
    params.forEach(x => {
        if (!x in resp)
            return `Expected "${x}" in response`;
    });
    if ('result' in resp && resp.result != 'ok') {
        if (resp.info)
            return resp.info;
        return `Service returned "${resp.result}" status`;
    }
    return '';
}

var refreshIntervalId;
var statusRecived = true;

function getTaskStatus() {
    //console.log(`getTaskStatus()`);
    if (!statusRecived)
        return;
    const els = document.getElementsByClassName('progress');
    for (let i = 0; i < els.length; i++) {
        const task_id = els[i].getAttribute('aria-task-id');
        const valuemax = els[i].getAttribute('aria-valuemax');
        if (task_id) {
            const api = `/api/logs/get_task_status/?format=json&task_id=${task_id}`;
            const callback = function() {
                if (this.readyState == 4) {
                    statusRecived = true;
                    if (this.status != 200) 
                        iziToast.error({title: `Create Task [${progress_id}]`, message: `${this.status}: ${this.statusText}`, position: 'bottomRight'});
                    else {
                        let resp = JSON.parse(this.responseText);
                        let mess = checkResp(resp, ['value', 'result']);
                        if (mess != '') {
                            iziToast.error({title: 'Get Task Status', message: mess, position: 'bottomRight'});
                            return;
                        }
                        //console.log(`value=${resp.value}`)
                        const pct = Math.round(resp.value / valuemax * 100);
                        els[i].children[0].style = `width: ${pct}%`;
                        els[i].parentElement.parentElement.parentElement.parentElement.children[1].innerText = resp.value;
                    }
                }
            };
            statusRecived = false;
            runAPI(api, callback);
        }
    }
}

function stopTask(progress_id, value, after_stop, info) {
    // console.log(`stopTask(progress_id=${progress_id}, value=${value})`);
    clearInterval(refreshIntervalId);
    el = document.getElementById(progress_id);
    if (el) {
        el.classList.add('d-none');
        el.parentElement.parentElement.children[1].classList.add('d-none');
        el.parentElement.parentElement.children[0].classList.remove('d-none');
        el.parentElement.parentElement.children[0].classList.remove('bi-circle');
        el.parentElement.parentElement.children[0].classList.add('bi-check-circle');
        el.parentElement.parentElement.parentElement.parentElement.children[1].innerText = value;
    }
    if (after_stop)
    after_stop(info);
}

function startTask(task_id, total, progress_id, after_stop) {
    // console.log(`startTask(task_id=${task_id}, total=${total}, progress_id=${progress_id})`);
    el = document.getElementById(progress_id);
    if (el) {
        el.setAttribute('aria-task-id', task_id);
        el.setAttribute('aria-valuemax', total);
        el.classList.remove('d-none');
        el.parentElement.parentElement.children[0].classList.add('d-none');
        el.parentElement.parentElement.children[1].classList.remove('d-none');
        refreshIntervalId = setInterval(getTaskStatus, 2000);
    }
    const api = `/api/logs/start_task/?format=json&task_id=${task_id}`;
    const callback = function() {
        if (this.readyState == 4) {
            if (this.status != 200)
                iziToast.error({title: `Create Task [${progress_id}]`, message: `${this.status}: ${this.statusText}`, position: 'bottomRight'});
            else {
                let resp = JSON.parse(this.responseText);
                let mess = checkResp(resp, ['value', 'result', 'info']);
                if (mess != '') {
                    iziToast.error({title: `Start Task [${progress_id}]`, message: mess, position: 'bottomRight'});
                    return;
                }
                stopTask(progress_id, resp.value, after_stop, resp.info);
            }
        } 
    };
    runAPI(api, callback);
}

function createTask(app, service, item_id, progress_id, after_stop) {
    // console.log(`createTask(app=${app}, service=${service}, item_id=${item_id}, progress_id=${progress_id})`);
    const api = `/api/logs/create_task/?format=json&app=${app}&service=${service}&item_id=${item_id}`;
    const callback = function() {
        if (this.readyState == 4) {
            if (this.status != 200) 
                iziToast.error({title: `Create Task [${progress_id}]`, message: `${this.status}: ${this.statusText}`, position: 'bottomRight'});
            else {
                let resp = JSON.parse(this.responseText);
                let mess = checkResp(resp, ['task_id', 'total', 'result']);
                if (mess != '') {
                    iziToast.error({title: `Create Task [${progress_id}]`, message: mess, position: 'bottomRight'});
                    return;
                }
                startTask(resp.task_id, resp.total, progress_id, after_stop);
            }
        }
    };
    runAPI(api, callback);
}

