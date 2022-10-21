let lat = document.getElementById("id_latitude");
let lon = document.getElementById("id_longitude");

if (lat && lon && !lat.value && ! lon.value && navigator.geolocation) {
    try {
        navigator.geolocation.getCurrentPosition(savePosition);
    }
    catch (error) {
        console.log(error);
    }
}

function savePosition(position) {
    lat.value = position.coords.latitude;
    lon.value = position.coords.longitude;
}