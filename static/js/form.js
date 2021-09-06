resize();

function resize()
{
    document.querySelectorAll('[data-autoresize]').forEach(function (element) {
        element.style.boxSizing = 'border-box';
        var offset = element.offsetHeight - element.clientHeight;
        element.style.minHeight = "25px";
        element.style.height = (element.scrollHeight + offset)+"px";
        element.addEventListener('input', function (event) {
            event.target.style.height = 'auto';
            event.target.style.height = event.target.scrollHeight+ offset + 'px';
        });
    element.removeAttribute('data-autoresize');
});
}
function closeForm() {
    let item_id = window.location.pathname.match( /\d+/ )[0];
    let redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/';
    let grp = document.getElementById("id_grp");
    if (grp && grp.value)
        redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/?view=list&lst=' + grp.value;
    window.location.href = redirect_url;
}

function delItem(app_name) {
    if (!confirm('Are you sure?'))
        return;

    let item_id = window.location.pathname.match( /\d+/ )[0];
    let redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/';
    let grp = document.getElementById("id_grp");
    if (grp && grp.value)
        redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/?view=list&lst=' + grp.value;

    const api = '/api/tasks/' + item_id + '/role_delete/?format=json&role=' + app_name;
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = redirect_url;
        }
    };

    xhttp.send();
}

function categoryDelete(category) {
    let item_id = window.location.pathname.match( /\d+/ )[0];
    let redirect_url = window.location.href;
    const api = '/api/tasks/' + item_id + '/category_delete/?format=json&category=' + category;
    let url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open('GET', url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = redirect_url;
        }
    };

    xhttp.send();
}