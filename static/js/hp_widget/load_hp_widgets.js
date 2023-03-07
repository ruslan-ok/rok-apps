document.querySelectorAll('.hp-widget').forEach(function(el) {
    const id = el.id.replace('id_hp_widget_', '');
    const api = '/api/get_widget/?id=' + id;
    const url = window.location.protocol + '//' + window.location.host + api;
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            el.innerHTML = xmlHttp.responseText;
            if (el.innerHTML == '')
                el.classList.add('d-none');
            else {
                const chartList = ['health', 'crypto', 'currency', 'weather'];
                if (chartList.includes(id))
                    buildChart(id);
            }
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send(null);
});

function buildChart(id) {
    const api = '/api/get_chart_data/?mark=' + id;
    const url = window.location.protocol + '//' + window.location.host + api;
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.responseType = 'json';
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            data = xmlHttp.response;
            const chartEl = document.getElementById(id + 'Chart');
            const ctx = chartEl.getContext('2d');
            new Chart(ctx, data);
            chartEl.parentNode.removeChild(chartEl.parentNode.firstElementChild);
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send(null);
}
