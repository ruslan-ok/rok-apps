resize();
moveLists();
initDays();
checkCompleted(0);

function resize()
{
    document.querySelectorAll('[data-autoresize]').forEach(function (element) {
        element.style.boxSizing = 'border-box';
        var offset = element.offsetHeight - element.clientHeight;
        element.style.minHeight = "25px";
        element.style.height = (element.scrollHeight + offset)+"px";
        element.addEventListener('input', function (event) {
            event.target.style.height = event.target.scrollHeight+ offset + 'px';
        });
        element.removeAttribute('data-autoresize');
    });
}

function moveLists() {
    let el_src = document.getElementById('url-list-src');
    let el_dst = document.getElementById('url-list-dst');
    if (el_src && el_dst)
        el_dst.appendChild(el_src); 
    el_src = document.getElementById('file-list-src');
    el_dst = document.getElementById('file-list-dst');
    if (el_src && el_dst)
        [...el_src.children].forEach((chl) => el_dst.appendChild(chl))
}

function closeForm() {
    let item_id = window.location.pathname.match( /\d+/ )[0];
    let redirect_url = window.location.href.replace('/' + item_id + '/', '/');
    window.location.href = redirect_url;
}

function runAPI(api, callback, method='GET') {
    const url = window.location.protocol + '//' + window.location.host + api;
    let xhttp = new XMLHttpRequest();
    xhttp.open(method, url, true);
    let y = document.getElementsByName('csrfmiddlewaretoken');
    let crsf = y[0].value; 
    xhttp.setRequestHeader('X-CSRFToken', crsf);
    xhttp.setRequestHeader('Content-type', 'application/json');
    xhttp.onreadystatechange = callback;
    xhttp.send();
}

function addItem(app, role) {
    const api = '/api/tasks/add_item/?format=json&app=' + app + '&role=' + role;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            let resp = JSON.parse(this.responseText);
            if (!resp || !resp.task_id) {
                let mess = 'Error';
                if (resp.mess)
                    mess += '\n' + resp.mess;
                alert(mess);
                return;
            }
            let url_parts = window.location.href.split('?');
            let redirect_url = url_parts[0] + resp.task_id + '/';
            if (url_parts.length > 1)
                redirect_url += '?' + url_parts[1];
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function showInfo(text) {
    let el = document.getElementById('infoModal');
    el.querySelectorAll('div.modal-body')[0].innerText = text;

    let message = new bootstrap.Modal(document.getElementById('infoModal'), {});
    message.show();
}

function delItemConfirm(role, ban, text) {
    if (ban) {
        showInfo(ban);
        return;
      }
    
    let el = document.getElementById('delModal');
    el.querySelectorAll('div.modal-body')[0].innerText = text;
    el.querySelectorAll('button.btn-danger')[0].onclick = function() {return delItem(role);}

    let conf = new bootstrap.Modal(document.getElementById('delModal'), {});
    conf.show();
}

function delItem(role) {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    let redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/';
    let grp = document.getElementById("id_grp");
    if (grp && grp.value)
        redirect_url = window.location.href.split('/' + item_id + '/')[0] + '/?group=' + grp.value;
    const api = '/api/tasks/' + item_id + '/role_delete/?format=json&role=' + role;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function delCategory(category) {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    const redirect_url = window.location.href;
    const api = '/api/tasks/' + item_id + '/category_delete/?format=json&category=' + category;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function delURL(url_id) {
    const api = '/api/urls/' + url_id + '/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 204) {
            console.log('URL deleted successfully.');
        }
    };
    runAPI(api, callback, 'DELETE');

    let el = document.getElementById('id_url_' + url_id);
    if (el) {
        el.parentElement.removeChild(el);
    }
}

function uploadFile()
{
    document.getElementById('id_upload').click();
}

function fileSelected()
{
    filename = document.getElementById('id_upload').files[0].name;
    fn_element = document.getElementById('loadFile');
    if (fn_element)
        fn_element.innerText = filename;
    document.getElementById('id_submit').click();
}

function delFile(app, role, fname, file_id) {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    const api = '/api/tasks/' + item_id + '/file_delete/?format=json&app=' + app + '&role=' + role + '&fname=' + fname;
    const callback = function() {
        if (this.readyState == 4 && this.status == 204) {
            console.log('deleted file ' + fname);
        }
    };
    runAPI(api, callback);

    let el = document.getElementById('id_file_' + file_id);
    if (el) {
        el.parentElement.removeChild(el);
    }
}

function getAvatar() {
    document.getElementById('id_avatar').click();
}

function avatarSelected()
{
    filename = document.getElementById('id_avatar').files[0].name;
    document.getElementById('id_submit').click();
}

function delAvatar() {
    const redirect_url = window.location.href;
    const api = '/api/profile/delete_avatar/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('deleted profile avatar');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function toggleCompleted(item_id) {
    const redirect_url = window.location.href;
    const api = '/api/tasks/' + item_id + '/completed/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function toggleImportant(item_id, redirect=true) {
    const redirect_url = window.location.href;
    const api = '/api/tasks/' + item_id + '/important/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            if (redirect)
                window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}


function toggleFormImportant() {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    let el = document.getElementById('toggle-important');
    let img = el.querySelectorAll('i')[0];
    let checked = el.hasAttribute('checked');
    if (checked) {
        el.removeAttribute('checked');
        img.classList.remove('bi-star-fill');
        img.classList.add('bi-star');
    }
    else {
        el.setAttribute('checked', '');
        img.classList.remove('bi-star');
        img.classList.add('bi-star-fill');
    }
    toggleImportant(item_id, false);
}

function apartChange(selectObject) {
    const value = selectObject.value;
    const redirect_url = window.location.href;
    const api = '/api/apart/' + value + '/set_active/?format=json';
    const callback = function() {
        if ((this.readyState == 4 || this.readyState == 2)  && this.status == 200) {
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function addRole(role) {
    const redirect_url = window.location.href;
    const item_id = window.location.pathname.match( /\d+/ )[0];
    const api = '/api/tasks/' + item_id + '/role_add/?format=json&role=' + role;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function delRole(role) {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    const redirect_url = window.location.href;
    const api = '/api/tasks/' + item_id + '/role_delete/?format=json&role=' + role;
    const callback = function() {
        if ((this.readyState == 4 || this.readyState == 2)  && this.status == 200) {
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function ToggleSelectField(name)
{
  var sel_id = name + '-select';
  document.getElementById(sel_id).classList.toggle('d-none');
}

function toggleMyDay() {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    let el = document.getElementById('toggle-myday');
    let img = el.querySelectorAll('i')[0];
    let selected = el.hasAttribute('selected');
    if (selected)
        el.removeAttribute('selected');
    else
        el.setAttribute('selected', '');
    
    const redirect_url = window.location.href;
    const api = '/api/tasks/' + item_id + '/in_my_day/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function completeStep(step_id) {
    let el = document.getElementById('step_edit_name_' + step_id);
    el.classList.toggle('completed');

    const api = '/api/steps/' + step_id + '/complete/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Step completion toggled.');
        }
    };
    runAPI(api, callback);
}

function delStep(step_id) {
    const api = '/api/steps/' + step_id + '/?format=json';
    const redirect_url = window.location.href;
    const callback = function() {
        if (this.readyState == 4 && this.status == 204) {
            console.log('Step deleted successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback, 'DELETE');
}

function delStepConfirm(step_id, text) {
    let el = document.getElementById('delModal');
    el.querySelectorAll('div.modal-body')[0].innerText = text;
    el.querySelectorAll('button.btn-danger')[0].onclick = function() {return delStep(step_id);}

    let conf = new bootstrap.Modal(document.getElementById('delModal'), {});
    conf.show();
    
}

function editStep(step_id, value) {
    const api = '/api/steps/' + step_id + '/rename/?format=json&value=' + value;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Step changes saved successfully.')
        }
    };
    runAPI(api, callback);
}

function delTermin(text) {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    let el = document.getElementById('id_termin_title');
    el.classList.remove('expired');
    el.classList.remove('actual');
    el.innerText = text;
    document.getElementById('id_termin_delete').classList.add('d-none');
    const frm = document.getElementById('article_form');
    frm.elements['stop'].value = '';
    const api = '/api/tasks/' + item_id + '/termin_delete/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Termin removed successfully.')
        }
    };
    runAPI(api, callback);

}

function terminToday() {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    const api = '/api/tasks/' + item_id + '/termin_today/?format=json';
    const redirect_url = window.location.href;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Termin set successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function terminTomorrow() {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    const api = '/api/tasks/' + item_id + '/termin_tomorrow/?format=json';
    const redirect_url = window.location.href;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Termin set successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function terminNextWeek() {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    const api = '/api/tasks/' + item_id + '/termin_next_week/?format=json';
    const redirect_url = window.location.href;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Termin set successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function delRepeat(text) {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    let el = document.getElementById('id_repeat_title');
    el.innerText = text;
    document.getElementById('id_repeat_delete').classList.add('d-none');
    const frm = document.getElementById('article_form');
    frm.elements['repeat'].value = '';
    const api = '/api/tasks/' + item_id + '/repeat_delete/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Repeat removed successfully.')
        }
    };
    runAPI(api, callback);
}

function repeatSet(mode) {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    let repeat = 0;
    let days = 0;
    switch (mode) {
        case 1:
            repeat = 1;
            break;
        case 2:
            repeat = 3;
            days = 31;
            break;
        case 3:
            repeat = 3;
            break;
        case 4:
            repeat = 4;
            break;
        case 5:
            repeat = 5;
            break;
    }
    const api = '/api/tasks/' + item_id + '/repeat_set/1/' + repeat + '/' + days + '/?format=json';
    const redirect_url = window.location.href;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Repeat set successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function initDays() {
  const frm = document.getElementById('article_form');
  if (!frm)
    return;
  const days = frm.elements['repeat_days'].value;
  if (!days)
    return;
  for (let i = 1; i <= 7; i++) {
    if ((days & (1 << (i-1))) != 0)
      document.getElementById('d' + i).classList.add('selected');
  }
}

function getDays() {
  let days = 0;
  for (let i = 1; i <= 7; i++) {
    if (document.getElementById('d' + i).classList.contains('selected'))
      days += (1 << (i-1));
  }
  return days;
}

function dayClick(_num) {
  let day = document.getElementById('d' + _num);
  day.classList.toggle('selected');
  const frm = document.getElementById('article_form');
  frm.elements['repeat_days'].value = getDays();
}

function delRemind(text) {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    let el = document.getElementById('id_remind_title');
    el.innerText = text;
    document.getElementById('id_remind_delete').classList.add('d-none');
    const frm = document.getElementById('article_form');
    frm.elements['remind'].value = '';
      const api = '/api/tasks/' + item_id + '/remind_delete/?format=json';
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Remind removed successfully.')
        }
    };
    runAPI(api, callback);
}

function remindToday() {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    const api = '/api/tasks/' + item_id + '/remind_today/?format=json';
    const redirect_url = window.location.href;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Remind set successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function remindTomorrow() {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    const api = '/api/tasks/' + item_id + '/remind_tomorrow/?format=json';
    const redirect_url = window.location.href;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Remind set successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function remindNextWeek() {
    const item_id = window.location.pathname.match( /\d+/ )[0];
    const api = '/api/tasks/' + item_id + '/remind_next_week/?format=json';
    const redirect_url = window.location.href;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Remind set successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}

function checkCompleted(mode) {
    cf = document.getElementById('id_completed');
    nf = document.getElementById('id_name');
    if (!cf || !nf)
        return;
    if (mode == 0)
        if (cf.hasAttribute('checked'))
            nf.classList.add('completed');
        else
            nf.classList.remove('completed');
    if (mode == 1)
        nf.classList.toggle('completed');
}

function toggleSubGroup(div, group_id, sub_group_id) {
    const hidden = document.getElementById('id-sub-group-' + sub_group_id).classList.toggle('d-none');
    if (hidden) {
        div.children[0].classList.remove('bi-chevron-down');
        div.children[0].classList.add('bi-chevron-right');
    } else {
        div.children[0].classList.remove('bi-chevron-right');
        div.children[0].classList.add('bi-chevron-down');
    }
    const api = '/api/groups/' + group_id + '/toggle_sub_group/?format=json&sub_group_id=' + sub_group_id;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Sub group ' + sub_group_id + ' toggled successfully.');
        }
    };
    runAPI(api, callback);
}

function setTheme(group_id, theme_id) {
    const redirect_url = window.location.href;
    const api = '/api/groups/' + group_id + '/set_theme/?format=json&theme_id=' + theme_id;
    const callback = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Theme ' + theme_id + ' setted successfully.');
            window.location.href = redirect_url;
        }
    };
    runAPI(api, callback);
}