const group_api = "http://localhost:8000/en/api/groups/";
const postfix = "format=json";

function addGroup() {
    let x = document.getElementById("new_group_id");
    let name = x.value;
    if (!name)
      return;
  
    x.value = '';
    let y = document.getElementsByName("csrfmiddlewaretoken");
    let crsf = y[0].value; 
  
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", group_api + "?" + postfix, true);
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader("Content-type", "application/json");
    
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 201) {
        list_id = JSON.parse(this.responseText).id;
        list_name = JSON.parse(this.responseText).name;
        createGroup(list_id, list_name);
      }
    };
  
    let data = {
        "app": app,
        "node": null,
        "name": encodeURI(name),
        "sort": "",
        "is_open": false,
        "is_leaf": true,
        "level": 0
    };

    xhttp.send(JSON.stringify(data));
}