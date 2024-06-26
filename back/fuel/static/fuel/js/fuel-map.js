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
  var map = L.map('map');
  
  L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);
  
  let gps_data = document.getElementById('gps_data').innerText;
  let gps_corr = gps_data.replace(/'/g,'"');
  let points = JSON.parse(gps_corr);

  if (points.length == 0) {
    map.setView([latitude, longitude], 7);
    return;
  }

  var markers = L.markerClusterGroup();
  
  for (i = 0; i < points.length; i++) {
    var a = points[i];
    var title = '<a href="' + a['url'] + '">' + a["name"] + '</a>';
    var marker = L.marker(new L.LatLng(a['lat'], a['lon']), {
      title: a["name"]
    });
    marker.bindPopup(title);
    markers.addLayer(marker);
  }

  map.addLayer(markers);
  map.fitBounds(markers.getBounds().pad(0.5), {maxZoom: 13});
}
