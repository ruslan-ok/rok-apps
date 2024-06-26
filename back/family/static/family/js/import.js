function hideActions() {
    els = document.getElementsByClassName('actions')
    if (els && els.length > 0)
        els[0].classList.add('d-none');
}

const importFinish = function(info) {
    console.log('import done: ' + info);
    tree_id = +info;
    redirect_url = window.location.href.split('/import/')[0] + `/${tree_id}/`;
    window.location.href = redirect_url;
};

const app = 'family';

const saveGedcom = function(info) {
    console.log('build Gedcom: ' + info);
    tree_id = +info;
    createTask(app, 'gedcom', tree_id, 'gedcom', importFinish); };

function importStart()
{
    let queryParams = new URLSearchParams(window.location.search);
    filename = queryParams.get('file');
    createTask(app, 'import', filename, 'import', saveGedcom);
}

hideActions();
importStart();
