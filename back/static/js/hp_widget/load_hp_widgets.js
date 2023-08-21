async function buildChart(id) {
    const api = '/api/get_chart_data/?mark=' + id;
    const url = window.location.protocol + '//' + window.location.host + api;
    const options = {
        method: 'GET',
        headers: {'Content-type': 'application/json'},
    };
    const response = await fetch(url, options);
    if (!response.ok)
        return;
    let data = await response.json();
    const chartEl = document.getElementById(id + 'Chart');
    if (chartEl) {
        const ctx = chartEl.getContext('2d');
        new Chart(ctx, data);
        chartEl.parentNode.removeChild(chartEl.parentNode.firstElementChild);
    }
}

async function loadWidget(widget) {
    const id = widget.id.replace('id_hp_widget_', '');
    const api = '/api/get_widget/?id=' + id;
    const url = window.location.protocol + '//' + window.location.host + api;
    const options = {method: 'GET',};
    const response = await fetch(url, options);

    if (!response.ok) {
        const mess = `HTTP error! Widget: ${id}, Status: ${response.status}`;
        iziToast.error({title: 'Error', message: mess, position: 'bottomRight'});
        throw new Error(mess);
    }
    let data = await response.text();
    if (data == '')
        widget.classList.add('d-none');
    else {
        widget.innerHTML = data;
        const chartList = ['health', 'crypto', 'currency', 'weather'];
        if (chartList.includes(id))
            buildChart(id);
    }
}

function loadAllWidgets() {
    const widgets = Array.from(document.querySelectorAll('.hp-widget'));
    for (const widget of widgets) {
        loadWidget(widget)
    }
}

loadAllWidgets();
