document.querySelectorAll('.hp-widget').forEach(function(el) {
    const id = el.id.replace('id_hp_widget_', '');
    const api = '/api/get_widget/?id=' + id;
    const url = window.location.protocol + '//' + window.location.host + api;
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200) {
            el.innerHTML = xmlHttp.responseText;
            if (id == 'health')
                buildChart('weight_last');
        }
    }
    xmlHttp.open("GET", url, true);
    xmlHttp.send(null);
});