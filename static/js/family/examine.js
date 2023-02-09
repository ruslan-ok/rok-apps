function hideActions() {
    els = document.getElementsByClassName('actions')
    if (els && els.length > 0)
        els[0].classList.add('d-none');
}

const app = 'family';
const item_id = window.location.pathname.match( /\d+/ )[0];
const examine_result = function(info) {
    let el = document.getElementById('examine-result');
    if (el)
        el.innerText = info;
};
const start_examine = function() { createTask(app, 'examine', item_id, 'examine', examine_result); };

hideActions();
createTask(app, 'export', item_id, 'export', start_examine);
