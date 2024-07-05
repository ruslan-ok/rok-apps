function buildChart(mark, filter = undefined) {
    let api = '/api/get_chart_data/?mark=' + mark;
    if (filter)
        api += '&filter=' + structuredClone(filter);
    const url = window.location.protocol + '//' + window.location.host + api;
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.responseType = 'json';
    xmlHttp.onreadystatechange = function () {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            let widget_data = xmlHttp.response;
            let chart = Chart.getChart("healthChart"); // <canvas> id
            if (chart != undefined) {
                chart.destroy();
            }
            const chartEl = document.getElementById('healthChart');
            const ctx = chartEl.getContext('2d');
            new Chart(ctx, widget_data.chart);
            if (chart == undefined)
                chartEl.parentNode.removeChild(chartEl.parentNode.firstElementChild);
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send(null);
}

function buildFilteredChart() {
    const filter = document.getElementById('id_incident');
    buildChart('temp', filter.value);
}

function initFilter() {
    const el = document.getElementById('id_incident');
    if (el)
        el.onchange = buildFilteredChart;
}
