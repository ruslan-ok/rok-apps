function runAPI(api, callback, method='GET') {
    const url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open(method, url, true);
    /*let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);*/
    xhttp.setRequestHeader('Content-type', 'application/json');
    xhttp.onreadystatechange = callback;
    xhttp.send();
}

function get_btc_price() {
    var el_amount = document.getElementById('btc_amount_id');
    if (!el_amount)
        return;
  
    const api = '/api/logs/get_btc_price/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            let obj = JSON.parse(this.response);
            if (obj.status == 'success') {
                el_amount.innerText = Math.round(parseFloat(0.07767845 * obj.data.price)).toLocaleString('ru-RU') + '$';
            }
        }
    };
    runAPI(api, callback);
}

get_btc_price();