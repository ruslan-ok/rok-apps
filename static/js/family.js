function setTree(id) {
    let searchParams = new URLSearchParams(window.location.search);
    searchParams.delete('indi');
    searchParams.set('tree', id);
    let href = window.location.href.split('?')[0] + 'refresh/?' + searchParams.toString();
    window.location.href = href;
}

function setPerson(id) {
    let searchParams = new URLSearchParams(window.location.search);
    searchParams.delete('tree');
    searchParams.set('indi', id);
    let href = window.location.href.split('?')[0] + 'refresh/?' + searchParams.toString();
    window.location.href = href;
}

function setDepth(value) {
    let searchParams = new URLSearchParams(window.location.search);
    searchParams.set('depth', value);
    let href = window.location.href.split('?')[0] + 'refresh/?' + searchParams.toString();
    window.location.href = href;
}

function updateMedia(tree_id) {
    const api = '/api/famtree/' + tree_id + '/update_media/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Media updated successfully.');
        }
    };
    runAPI(api, callback);
}

function runAPI(api, callback, method='GET') {
    const url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open(method, url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');
    xhttp.onreadystatechange = callback;
    xhttp.send();
}

function makeDraggable(evt) {
    var svg = evt.target;
    svg.addEventListener('mousedown', startDrag);
    svg.addEventListener('mousemove', drag);
    svg.addEventListener('mouseup', endDrag);
    svg.addEventListener('mouseleave', endDrag);
    var selectedElement = false;
    function startDrag(evt) {
        if (evt.target.nodeName == 'svg') {
            selectedElement = document.getElementById('draggable');
        }
    }
    function drag(evt) {
        if (selectedElement) {
            evt.preventDefault();
            let value = selectedElement.attributes.transform.value;
            const args = value.split('(')[1].split(')')[0];
            let x = parseInt(args.split(',')[0]);
            let y = parseInt(args.split(',')[1]);
            x = x + evt.movementX;
            y = y + evt.movementY;
            value = 'translate('+ x + ', ' + y + ')';
            selectedElement.attributes.transform.value = value;
          }
    }
    function endDrag(evt) {
        selectedElement = null;
    }
  }

function individualDetail(tree_id, indi_id) {
    window.location = `/family/${tree_id}/individual/${indi_id}/`;
}

function zoomIn() {
    console.log('The "zoomIn()"  function is not implemented.')
}

function zoomOut() {
    console.log('The "zoomOut()"  function is not implemented.')
}