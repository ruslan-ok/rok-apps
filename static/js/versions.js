get_bootstrap_version();

function get_bootstrap_version() {
    const ver = bootstrap.Tooltip.VERSION;
    if (ver) {
        el = document.getElementById('id_bootstrap_version');
        el.innerText = ver;
    }
}