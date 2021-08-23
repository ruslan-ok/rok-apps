const group_api = '/ru/api/groups/';
const postfix = 'format=json';

function addGroup(app) {
    let x = document.getElementById('new_group_id');
    let name = x.value;
    if (!name)
      return;
  
    x.value = '';
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
  
    let url = window.location.protocol + '//' + window.location.host + group_api + '?' + postfix;
    let xhttp = new XMLHttpRequest();
    xhttp.open('POST', url, true);
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');
    
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 201) {
        list_id = JSON.parse(this.responseText).id;
        list_name = JSON.parse(this.responseText).name;
        list_url = `${window.location.protocol}//${window.location.host}/${app}/?view=list&lst=${list_id}`;
        window.location.href = list_url;
      }
    };
  
    let data = {
        'app': app,
        'node': null,
        'name': encodeURI(name),
        'sort': ''
    };

    xhttp.send(JSON.stringify(data));
}

function delGroup() {
  if (!confirm('Are you sure?'))
    return;
  let id = window.location.pathname.match( /\d+/ )[0];
  let url = window.location.protocol + '//' + window.location.host + group_api + id + '/?' + postfix;
  let redirect_url = window.location.href.split('/group/')[0] + '/';
  let xhttp = new XMLHttpRequest();
  xhttp.open('DELETE', url, true);
  let y = document.getElementsByName('csrfmiddlewaretoken');
  let crsf = y[0].value; 
  xhttp.setRequestHeader('X-CSRFToken', crsf);
  xhttp.setRequestHeader('Content-type', 'application/json');
  
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 204) {
      window.location.href = redirect_url;
    }
  };

  xhttp.send();
}
