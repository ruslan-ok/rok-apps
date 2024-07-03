function showInfo(text) {
    let el = document.getElementById('infoModal');
    el.querySelectorAll('div.modal-body')[0].innerText = text;

    let message = new bootstrap.Modal(document.getElementById('infoModal'), {});
    message.show();
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

function addPrice(apart_id) {
    const service = document.getElementById('id_new_service');
    const value = service.options[service.selectedIndex].value;
    if (!value) {
        showInfo('Select service.');
        return;
    }
    let param_serv = '&service_id=' + value;
    let param_group = '&group_id=' + apart_id;
    const api = '/api/tasks/add_item?format=json&app=apart&role=price' + param_serv + param_group;
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

function refreshTab(tab) {
    let parser = document.createElement('a');
    parser.href = window.location.href;
    let params = new URLSearchParams(parser.search);
    params.set('tab', tab);
    parser.search = params.toString();
    if (window.location.href == parser.href)
        location.reload();
    else
        window.location.href = parser.href;
}

const addMeter = document.getElementById('addMeter');

if (addMeter) {
    addMeter.addEventListener('show.bs.modal', event => {
      const button = event.relatedTarget;
      const meter_apart = button.getAttribute('data-bs-apart');
      addMeter.querySelector('#id_add_meter_apart').value = `${meter_apart}`;
    })
  }
  
  async function addApartMeter(django_host_api) {
    const dt_from = addMeter.querySelector('#id_add_meter_from').value;
    const dt_until = addMeter.querySelector('#id_add_meter_until').value;
    const sel = addMeter.querySelector('#id-add_select-meter');
    const data = {
        task_1: +addMeter.querySelector('#id_add_meter_apart').value,
        code: sel.value,
        sort: addMeter.querySelector('#id_add_meter_sort').value,
        dt_from: dt_from ? dt_from : null,
        dt_until: dt_until ? dt_until : null,
        value: addMeter.querySelector('#id_add_meter_value').value
    };

    const url = `${django_host_api}/api/apart/property/meter/`;
    const crsf = document.getElementsByName('csrfmiddlewaretoken')[0].value; 
    const options = {
        method: 'POST',
        headers: {
            'X-CSRFToken': crsf,
            'Content-type': 'application/json'
        },
        body: JSON.stringify(data),
    };

    await fetch(url, options)
        .then((response) => {
            if (!response.ok) {
                const mess = `HTTP error! Status: ${response.status}`;
                iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
                throw new Error(mess);
            }
            refreshTab('meter');
        });
}

const editMeter = document.getElementById('editMeter');

if (editMeter) {
  editMeter.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    const meter_id = button.getAttribute('data-bs-id');
    const meter_apart = button.getAttribute('data-bs-apart');
    const meter_code = button.getAttribute('data-bs-code');
    const meter_sort = button.getAttribute('data-bs-sort');
    const meter_name = button.getAttribute('data-bs-name');
    const meter_value = button.getAttribute('data-bs-value').replace(',', '.');
    const meter_from = button.getAttribute('data-bs-from');
    const meter_until = button.getAttribute('data-bs-until');

    editMeter.querySelector('#id_edit_meter_id').value = `${meter_id}`;
    editMeter.querySelector('#id_edit_meter_apart').value = `${meter_apart}`;
    editMeter.querySelector('#id_edit_meter_code').value = `${meter_code}`;
    editMeter.querySelector('#id_edit_meter_sort').value = `${meter_sort}`;
    editMeter.querySelector('#id_edit_meter_name').value = `${meter_name}`;
    editMeter.querySelector('#id_edit_meter_value').value = `${meter_value}`;
    editMeter.querySelector('#id_edit_meter_from').value = `${meter_from}`;
    editMeter.querySelector('#id_edit_meter_until').value = `${meter_until}`;
  })
}

async function saveApartMeter(django_host_api) {
    const dt_from = editMeter.querySelector('#id_edit_meter_from').value;
    const dt_until = editMeter.querySelector('#id_edit_meter_until').value;
    const data = {
        id: +editMeter.querySelector('#id_edit_meter_id').value,
        task_1: +editMeter.querySelector('#id_edit_meter_apart').value,
        code: editMeter.querySelector('#id_edit_meter_code').value,
        sort: editMeter.querySelector('#id_edit_meter_sort').value,
        dt_from: dt_from ? dt_from : null,
        dt_until: dt_until ? dt_until : null,
        value: editMeter.querySelector('#id_edit_meter_value').value
    };

    const url = `${django_host_api}/en/api/apart/property/meter/${data.id}/`;
    const crsf = document.getElementsByName('csrfmiddlewaretoken')[0].value; 
    const options = {
        method: 'PUT',
        headers: {
            'X-CSRFToken': crsf,
            'Content-type': 'application/json'
        },
        body: JSON.stringify(data),
    };

    await fetch(url, options)
        .then((response) => {
            if (!response.ok) {
                const mess = `HTTP error! Status: ${response.status}`;
                iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
                throw new Error(mess);
            }
            refreshTab('meter');
        });
}

async function deleteApartMeter(django_host_api) {
    const apart_meter_id = +editMeter.querySelector('#id_edit_meter_id').value;
    const url = `${django_host_api}/api/apart/property/meter/${apart_meter_id}/`;
    const crsf = document.getElementsByName('csrfmiddlewaretoken')[0].value; 
    const options = {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': crsf,
            'Content-type': 'application/json'
        },
    };

    await fetch(url, options)
        .then((response) => {
            if (!response.ok) {
                const mess = `HTTP error! Status: ${response.status}`;
                iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
                throw new Error(mess);
            }
            refreshTab('meter');
        });
}

const addService = document.getElementById('addService');

if (addService) {
    addService.addEventListener('show.bs.modal', event => {
      const button = event.relatedTarget;
      const service_apart = button.getAttribute('data-bs-apart');
      addService.querySelector('#id_add_service_apart').value = `${service_apart}`;
    })
  }
  
  async function addApartService(django_host_api) {
    const dt_from = addService.querySelector('#id_add_service_from').value;
    const dt_until = addService.querySelector('#id_add_service_until').value;
    const sel = addService.querySelector('#id-select-service');
    const data = {
        task_1: +addService.querySelector('#id_add_service_apart').value,
        code: sel.value,
        sort: addService.querySelector('#id_add_service_sort').value,
        dt_from: dt_from ? dt_from : null,
        dt_until: dt_until ? dt_until : null,
    };

    const url = `${django_host_api}/api/apart/property/service/`;
    const crsf = document.getElementsByName('csrfmiddlewaretoken')[0].value; 
    const options = {
        method: 'POST',
        headers: {
            'X-CSRFToken': crsf,
            'Content-type': 'application/json'
        },
        body: JSON.stringify(data),
    };

    await fetch(url, options)
        .then((response) => {
            if (!response.ok) {
                const mess = `HTTP error! Status: ${response.status}`;
                iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
                throw new Error(mess);
            }
            refreshTab('service');
        });
}

const editService = document.getElementById('editService');

if (editService) {
  editService.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    const service_id = button.getAttribute('data-bs-id');
    const service_apart = button.getAttribute('data-bs-apart');
    const service_code = button.getAttribute('data-bs-code');
    const service_sort = button.getAttribute('data-bs-sort');
    const service_name = button.getAttribute('data-bs-name');
    const service_from = button.getAttribute('data-bs-from');
    const service_until = button.getAttribute('data-bs-until');

    editService.querySelector('#id_edit_service_id').value = `${service_id}`;
    editService.querySelector('#id_edit_service_apart').value = `${service_apart}`;
    editService.querySelector('#id_edit_service_code').value = `${service_code}`;
    editService.querySelector('#id_edit_service_sort').value = `${service_sort}`;
    editService.querySelector('#id_edit_service_name').value = `${service_name}`;
    editService.querySelector('#id_edit_service_from').value = `${service_from}`;
    editService.querySelector('#id_edit_service_until').value = `${service_until}`;
  })
}

async function saveApartService(django_host_api) {
    const dt_from = editService.querySelector('#id_edit_service_from').value;
    const dt_until = editService.querySelector('#id_edit_service_until').value;
    const data = {
        id: +editService.querySelector('#id_edit_service_id').value,
        task_1: +editService.querySelector('#id_edit_service_apart').value,
        code: editService.querySelector('#id_edit_service_code').value,
        sort: editService.querySelector('#id_edit_service_sort').value,
        dt_from: dt_from ? dt_from : null,
        dt_until: dt_until ? dt_until : null,
    };

    const url = `${django_host_api}/api/apart/property/service/${data.id}/`;
    const crsf = document.getElementsByName('csrfmiddlewaretoken')[0].value; 
    const options = {
        method: 'PUT',
        headers: {
            'X-CSRFToken': crsf,
            'Content-type': 'application/json'
        },
        body: JSON.stringify(data),
    };

    await fetch(url, options)
        .then((response) => {
            if (!response.ok) {
                const mess = `HTTP error! Status: ${response.status}`;
                iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
                throw new Error(mess);
            }
            refreshTab('service');
        });
}

async function deleteApartService(django_host_api) {
    const apart_service_id = +editService.querySelector('#id_edit_service_id').value;
    const url = `${django_host_api}/api/apart/property/service/${apart_service_id}/`;
    const crsf = document.getElementsByName('csrfmiddlewaretoken')[0].value; 
    const options = {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': crsf,
            'Content-type': 'application/json'
        },
    };

    await fetch(url, options)
        .then((response) => {
            if (!response.ok) {
                const mess = `HTTP error! Status: ${response.status}`;
                iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
                throw new Error(mess);
            }
            refreshTab('service');
        });
}

const editMeterValue = document.getElementById('editMeterValue');

if (editMeterValue) {
    editMeterValue.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    const meter_id = button.getAttribute('data-bs-id');
    const meter_apart = button.getAttribute('data-bs-apart');
    const meter_period = button.getAttribute('data-bs-period');
    const meter_code = button.getAttribute('data-bs-code');
    const meter_name = button.getAttribute('data-bs-name');
    const meter_value = button.getAttribute('data-bs-value'); // .replace(',', '.');
    const meter_event = button.getAttribute('data-bs-event');

    editMeterValue.querySelector('#id_edit_meter_id').value = `${meter_id}`;
    editMeterValue.querySelector('#id_edit_meter_apart').value = `${meter_apart}`;
    editMeterValue.querySelector('#id_edit_meter_period').value = `${meter_period}`;
    editMeterValue.querySelector('#id_edit_meter_code').value = `${meter_code}`;
    editMeterValue.querySelector('#id_edit_meter_name').value = `${meter_name}`;
    editMeterValue.querySelector('#id_edit_meter_value').value = `${meter_value}`;
    editMeterValue.querySelector('#id_edit_meter_event').value = `${meter_event}`;
  })
}

async function saveMeterValue(django_host_api) {
    const dt_event = editMeterValue.querySelector('#id_edit_meter_event').value;
    const data = {
        id: +editMeterValue.querySelector('#id_edit_meter_id').value,
        task_1: +editMeterValue.querySelector('#id_edit_meter_apart').value,
        code: editMeterValue.querySelector('#id_edit_meter_code').value,
        period: editMeterValue.querySelector('#id_edit_meter_period').value + '-01',
        event: dt_event ? dt_event : null,
        value: editMeterValue.querySelector('#id_edit_meter_value').value
    };

    const url = `${django_host_api}/api/apart/period/meter_value/${data.id}/`;
    const crsf = document.getElementsByName('csrfmiddlewaretoken')[0].value; 
    const options = {
        method: 'PUT',
        headers: {
            'X-CSRFToken': crsf,
            'Content-type': 'application/json'
        },
        body: JSON.stringify(data),
    };

    await fetch(url, options)
        .then((response) => {
            if (!response.ok) {
                const mess = `HTTP error! Status: ${response.status}`;
                iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
                throw new Error(mess);
            }
            refreshTab('meter');
        });
}


const editServiceAmount = document.getElementById('editServiceAmount');

if (editServiceAmount) {
    editServiceAmount.addEventListener('show.bs.modal', event => {
    const button = event.relatedTarget;
    const service_id = button.getAttribute('data-bs-id');
    const service_apart = button.getAttribute('data-bs-apart');
    const service_period = button.getAttribute('data-bs-period');
    const service_code = button.getAttribute('data-bs-code');
    const service_name = button.getAttribute('data-bs-name');
    const service_tariff = button.getAttribute('data-bs-tariff').replace(',', '.');
    const service_accrued = button.getAttribute('data-bs-accrued').replace(',', '.');
    const service_payment = button.getAttribute('data-bs-payment').replace(',', '.');
    const service_event = button.getAttribute('data-bs-event');

    editServiceAmount.querySelector('#id_edit_service_id').value = `${service_id}`;
    editServiceAmount.querySelector('#id_edit_service_apart').value = `${service_apart}`;
    editServiceAmount.querySelector('#id_edit_service_period').value = `${service_period}`;
    editServiceAmount.querySelector('#id_edit_service_code').value = `${service_code}`;
    editServiceAmount.querySelector('#id_edit_service_name').value = `${service_name}`;
    editServiceAmount.querySelector('#id_edit_service_tariff').value = `${service_tariff}`;
    editServiceAmount.querySelector('#id_edit_service_accrued').value = `${service_accrued}`;
    editServiceAmount.querySelector('#id_edit_service_payment').value = `${service_payment}`;
    editServiceAmount.querySelector('#id_edit_service_event').value = `${service_event}`;
  })
}

async function saveServiceAmount(django_host_api) {
    const dt_event = editServiceAmount.querySelector('#id_edit_service_event').value;
    const data = {
        id: +editServiceAmount.querySelector('#id_edit_service_id').value,
        task_1: +editServiceAmount.querySelector('#id_edit_service_apart').value,
        code: editServiceAmount.querySelector('#id_edit_service_code').value,
        period: editServiceAmount.querySelector('#id_edit_service_period').value + '-01',
        event: dt_event ? dt_event : null,
        tariff: editServiceAmount.querySelector('#id_edit_service_tariff').value,
        accrued: editServiceAmount.querySelector('#id_edit_service_accrued').value,
        payment: editServiceAmount.querySelector('#id_edit_service_payment').value,
    };

    const url = `${django_host_api}/api/apart/period/service_amount/${data.id}/`;
    const crsf = document.getElementsByName('csrfmiddlewaretoken')[0].value; 
    const options = {
        method: 'PUT',
        headers: {
            'X-CSRFToken': crsf,
            'Content-type': 'application/json'
        },
        body: JSON.stringify(data),
    };

    await fetch(url, options)
        .then((response) => {
            if (!response.ok) {
                const mess = `HTTP error! Status: ${response.status}`;
                iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
                throw new Error(mess);
            }
            refreshTab('service');
        });
}

