


let mymap;

getLocation();

function getLocation() {
  if (navigator.geolocation)
    navigator.geolocation.getCurrentPosition(showPosition, showLondon);
}

function showPosition(position) {
  showMap(position.coords.latitude, position.coords.longitude);
}

function showLondon(err) {
  showMap(51.505, -0.09);
}

function showMap(latitude, longitude)
{
  mymap = L.map('mapid');

  let gps_data = document.getElementById('id_data').value;
  let gps_corr = gps_data.replace(/'/g,'"');
  let photos = JSON.parse(gps_corr);
  
  if (photos.length == 0)
    mymap.setView([latitude, longitude], 7);
  else
    if (photos.length == 1)
      mymap.setView([photos[0]["lat"], photos[0]["lon"]], 11); // Чем больше, тем ближе
    else
    {
      let corner1 = L.latLng(photos[0]["lat"], photos[0]["lon"]),
      corner2 = L.latLng(photos[1]["lat"], photos[1]["lon"]),
      bounds = L.latLngBounds(corner1, corner2);  
      for (i = 2; i < photos.length; i++) {
        bounds.extend([photos[i]["lat"], photos[i]["lon"]]);
      }
      mymap.fitBounds(bounds);
    }

  L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
    attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox/streets-v11',
    tileSize: 512,
    zoomOffset: -1,
    accessToken: 'pk.eyJ1IjoicnVzbGFuLW9rIiwiYSI6ImNrYmlkYjZ2NzBjMTYydHFpOWZqbm1lbDEifQ.dIV9rLOkKDBE7GzJplVzRA'
  }).addTo(mymap);

  for (i = 0; i < photos.length; i++) {
    let marker = L.marker([photos[i]["lat"], photos[i]["lon"]]).addTo(mymap);
    marker.bindPopup(photos[i]["name"] + "<br><a href='/photo/by_id/" + photos[i]["id"] + "/'><img src='/photo/get_mini/" + photos[i]["id"] + "/'>").openPopup();
  }
}
