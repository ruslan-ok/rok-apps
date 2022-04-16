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