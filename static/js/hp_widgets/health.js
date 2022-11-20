const scripts = [
    'https://cdn.jsdelivr.net/npm/chart.js',
];

scripts.forEach(x => {
    let script = document.createElement('script');
    script.src = x;
    document.body.appendChild(script);
})

function buildChart(mark) {
    const api = '/api/get_chart_data/?mark=' + mark;
    const url = window.location.protocol + '//' + window.location.host + api;
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.responseType = 'json';
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            data = xmlHttp.response;
            const chartEl = document.getElementById('healthChart');
            const ctx = chartEl.getContext('2d');
            new Chart(ctx, data);
            chartEl.parentNode.removeChild(chartEl.parentNode.firstElementChild);
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send(null);
}
