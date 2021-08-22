const host = "http://localhost:8000";
const group_api = "/en/api/groups/";
const postfix = "format=json";

function addGroup(app) {
    let x = document.getElementById("new_group_id");
    let name = x.value;
    if (!name)
      return;
  
    x.value = '';
    let y = document.getElementsByName("csrfmiddlewaretoken");
    let crsf = y[0].value; 
  
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", host + group_api + "?" + postfix, true);
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader("Content-type", "application/json");
    
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 201) {
        list_id = JSON.parse(this.responseText).id;
        list_name = JSON.parse(this.responseText).name;
        list_url = `${host}/${app}/?view=list&lst=${list_id}`;
        window.location.href = list_url;
      }
    };
  
    let data = {
        "app": app,
        "node": null,
        "name": encodeURI(name),
        "sort": ""
    };

    xhttp.send(JSON.stringify(data));
}