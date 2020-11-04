


var mymap;

getLocation();

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else {
    showMap(51.505, -0.09);
  }
}

function showPosition(position) {
  showMap(position.coords.latitude, position.coords.longitude);
}

function showMap(latitude, longitude)
{
  mymap = L.map('mapid').setView([latitude, longitude], 7);

  L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoicnVzbGFuLW9rIiwiYSI6ImNrYmlkYjZ2NzBjMTYydHFpOWZqbm1lbDEifQ.dIV9rLOkKDBE7GzJplVzRA'
  }).addTo(mymap);
  element = document.getElementById('id_data');
  var sgps = element.value;
  var sgps2 = sgps.replace(/'/g,'"');
  var photos = JSON.parse(sgps2);
  //alert(photos.length);
  for (i = 0; i < photos.length; i++) {
    L.marker([photos[i]["lat"], photos[i]["lon"]]).addTo(mymap);
  }
}
