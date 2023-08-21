getBootstrapVersion();
getLeafletVersion();
getChartVersion();

function getBootstrapVersion() {
    const ver = bootstrap.Tooltip.VERSION;
    if (ver) {
        el = document.getElementById('id_bootstrap_version');
        el.innerText = ver;
    }
}

function getLeafletVersion() {
    const ver = L.version;
    if (ver) {
        el = document.getElementById('id_leaflet_version');
        el.innerText = ver;
    }
}

function getChartVersion() {
    const ver = Chart.version;
    if (ver) {
        el = document.getElementById('id_chartjs_version');
        el.innerText = ver;
    }
}
