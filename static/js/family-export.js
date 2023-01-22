function hideActions() {
    els = document.getElementsByClassName('actions')
    if (els && els.length > 0)
        els[0].classList.add('d-none');
}

const app = 'family';
const item_id = window.location.pathname.match( /\d+/ )[0];

const exportFinish = function() {
    window.location.href = window.location.href + 'file/';
};

hideActions();
createTask(app, 'export', item_id, 'export', exportFinish);
