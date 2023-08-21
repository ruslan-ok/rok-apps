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

function getQueryVariable(variable) {
  var query = window.location.search.substring(1);
  var vars = query.split('&');
  for (var i = 0; i < vars.length; i++) {
      var pair = vars[i].split('=');
      if (decodeURIComponent(pair[0]) == variable) {
          return decodeURIComponent(pair[1]);
      }
  }
  console.log('Query variable %s not found', variable);
  return '';
}

function showMap(latitude, longitude)
{
  var map = L.map('mapid');

  let gps_data = document.getElementById('id_data').value;
  let gps_corr = gps_data.replace(/'/g,'"');
  let photos = JSON.parse(gps_corr);

  L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);
  
  if (photos.length == 0) {
    map.setView([latitude, longitude], 7);
    return;
  }

  const folder = getQueryVariable('folder');
  var markers = L.markerClusterGroup();
  
  for (i = 0; i < photos.length; i++) {
    var a = photos[i];
    var title = a["name"] + '<br><a href="/photo/image/?folder=' + folder + '&photo_num=' + a["num"] + '"><img src="/photo/get_mini/' + a["id"] + '">';
    var marker = L.marker(new L.LatLng(a['lat'], a['lon']));
    marker.bindPopup(title);
    markers.addLayer(marker);
  }

  map.addLayer(markers);
  map.fitBounds(markers.getBounds().pad(0.5), {maxZoom: 13});
}
