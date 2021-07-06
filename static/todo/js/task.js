const task_api = "http://localhost:8000/en/api/tasks/";
const step_api = "http://localhost:8000/en/api/steps/";
const group_api = "http://localhost:8000/en/api/groups/";
const postfix = "format=json";

document.getElementById('remind-select').style.display = "none";
document.getElementById('termin-select').style.display = "none";
document.getElementById('repeat-select').style.display = "none";
initDays();

//-----------------------------------------------------------------
// Common functions

// Getting the id of the item being edited
function getItemId() {
  return document.getElementById("article_form").dataset.item_id;
}

function toggleSelectField(name) {
  let sel_id = name + '-select';
  if (document.getElementById(sel_id).style.display == "none")
    document.getElementById(sel_id).style.display = "block";
  else
    document.getElementById(sel_id).style.display = "none";
}

function afterCalendarChanged(init, field) {
  if ((field == 1) || (field == 0)) {
    let dt = document.getElementById("id_remind_0");
    let tm = document.getElementById("id_remind_1");
    setRemind(dt.value, tm.value);
  }
  if ((field == 2) || (field == 0)) {
    let dt = document.getElementById("id_stop_0");
    let tm = document.getElementById("id_stop_1");
    setTermin(dt.value, tm.value);
  }
}

//-----------------------------------------------------------------
// Completed

function toggleCompleted() {
  let x = document.getElementById("task-completed");
  if (x.dataset.value.toLowerCase() == "true")
    x.dataset.value = "false";
  else
    x.dataset.value = "true";

  let xhttp = new XMLHttpRequest();
  xhttp.open("GET", task_api + getItemId() + "/completed/?" + postfix, true);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      if (x.dataset.value.toLowerCase() == "true") {
        x.children[0].setAttribute('src', '/static/todo/icon/complete.png');
        x.parentNode.children[1].classList.add("completed");
        x.parentNode.children[2].classList.add("completed");
      } else {
        x.children[0].setAttribute('src', '/static/todo/icon/uncomplete.png');
        x.parentNode.children[1].classList.remove("completed");
        x.parentNode.children[2].classList.remove("completed");
      }
    }
  };

  xhttp.send();
}

//-----------------------------------------------------------------
// Important

function toggleImportant() {
  let x = document.getElementById("task-important");
  if (x.dataset.value.toLowerCase() == "true")
    x.dataset.value = "false";
  else
    x.dataset.value = "true";

  let xhttp = new XMLHttpRequest();
  xhttp.open("GET", task_api + getItemId() + "/important/?" + postfix, true);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      if (x.dataset.value.toLowerCase() == "true")
        x.children[0].setAttribute('src', '/static/todo/icon/important-on.png');
      else
        x.children[0].setAttribute('src', '/static/todo/icon/important-off.png');
    }
  };

  xhttp.send();
}

//-----------------------------------------------------------------
// My Day

// Button "My day" click handling
function toggleMyDay() {
  let x = document.getElementById("myday");
  let value = x.classList.contains("selected");
  x.classList.toggle("selected");
  
  let xhttp = new XMLHttpRequest();
  xhttp.open("GET", task_api + getItemId() + "/in_my_day/?" + postfix, true);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      x.innerHTML = JSON.parse(this.responseText).title;
    }
  };

  xhttp.send();
}

//-----------------------------------------------------------------
// Termin and Remind common

function changeDateTime(mode, entity) {
  let x = document.getElementById(entity + "-view");
  let y = x.childNodes[1].childNodes[1].childNodes[3].childNodes[1];

  switch (mode) {
    case 0: func = entity + "_delete"; break;
    case 1: func = entity + "_today"; break;
    case 2: func = entity + "_tomorrow"; break;
    case 3: func = entity + "_next_week"; break;
  }
  
  y.childNodes[1].classList.remove("expired");
  if (mode == 0) {
    y.childNodes[1].classList.remove("actual");
    x.childNodes[1].childNodes[3].classList.add("hide");
  } else {
    y.childNodes[1].classList.add("actual");
    x.childNodes[1].childNodes[3].classList.remove("hide");
    toggleSelectField(entity);
  }

  let xhttp = new XMLHttpRequest();
  xhttp.open("GET", task_api + getItemId() + "/" + func + "/?" + postfix, true);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      y.childNodes[1].innerHTML = JSON.parse(this.responseText).date;
      y.childNodes[3].innerHTML = JSON.parse(this.responseText).time;
    }
  };

  xhttp.send();
}

function setDateTime(dt, tm, entity) {
  let x = document.getElementById(entity + "-view");
  let y = x.childNodes[1].childNodes[1].childNodes[3].childNodes[1];

  y.childNodes[1].classList.add("actual");
  x.childNodes[1].childNodes[3].classList.remove("hide");

  let xhttp = new XMLHttpRequest();
  xhttp.open("GET", task_api + getItemId() + "/" + entity + "_set/" + dt + "/" + tm + "/?" + postfix, true);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      y.childNodes[1].innerHTML = JSON.parse(this.responseText).date;
      y.childNodes[3].innerHTML = JSON.parse(this.responseText).time;
    }
  };

  xhttp.send();
}

//-----------------------------------------------------------------
// Termin

function changeTermin(mode) {
  changeDateTime(mode, "termin");
}

function setTermin(dt, tm) {
  setDateTime(dt, tm, "termin")
}

//-----------------------------------------------------------------
// Remind

function changeRemind(mode) {
  changeDateTime(mode, "remind");
}

function setRemind(dt, tm) {
  setDateTime(dt, tm, "remind")
}

//-----------------------------------------------------------------
// Repeat

function changeRepeat(_repeat, _workdays) {
  let ndx;
  switch(_repeat) {
    case 0: ndx = 0; break;
    case 1: ndx = 1; break;
    case 3: ndx = 2; break;
    case 4: ndx = 3; break;
    case 5: ndx = 4; break;
    default: ndx = 0;
  }
  
  if (_workdays) {
    let frm = document.getElementById('article_form');
    frm.elements['repeat_days'].value = 31;
    initDays();
  }

  let x = document.getElementById("repeat-view");
  let y = x.childNodes[1].childNodes[1].childNodes[3].childNodes[1];

  document.getElementById("id_repeat").selectedIndex = ndx;
  if (_repeat == 0) {
    y.childNodes[1].classList.remove("actual");
    x.childNodes[1].childNodes[3].classList.add("hide");
  } else {
    document.getElementById("id_repeat_num").value = 1;
    y.childNodes[1].classList.add("actual");
    x.childNodes[1].childNodes[3].classList.remove("hide");
    checkDaysVisible();
    toggleSelectField("repeat");
  }

  switch (_repeat) {
    case 0: func = "repeat_delete"; break;
    case 1: func = "repeat_daily"; break;
    case 3:
      if (_workdays)
        func = "repeat_workdays";
      else
        func = "repeat_weekly";
      break;
    case 4: func = "repeat_monthly"; break;
    case 5: func = "repeat_annually"; break;
  }
  
  let xhttp = new XMLHttpRequest();
  xhttp.open("GET", task_api + getItemId() + "/" + func + "/?" + postfix, true);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      y.childNodes[1].innerHTML = JSON.parse(this.responseText).title;
      y.childNodes[3].innerHTML = JSON.parse(this.responseText).info;
    }
  };

  xhttp.send();
}

function setRepeat() {
  let x = document.getElementById("repeat-view");
  let y = x.childNodes[1].childNodes[1].childNodes[3].childNodes[1];

  y.childNodes[1].classList.add("actual");
  x.childNodes[1].childNodes[3].classList.remove("hide");
  checkDaysVisible();
  
  let num = document.getElementById("id_repeat_num").value;
  let per = document.getElementById("id_repeat").selectedIndex + 1;
  let days = getDays();

  let xhttp = new XMLHttpRequest();
  xhttp.open("GET", task_api + getItemId() + "/repeat_set/" + num + "/" + per + "/" + days + "/?" + postfix, true);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      y.childNodes[1].innerHTML = JSON.parse(this.responseText).title;
      y.childNodes[3].innerHTML = JSON.parse(this.responseText).info;
    }
  };

  xhttp.send();
}

//-----------------------------------------------------------------
// Repeat Days

function initDays() {
  let frm = document.getElementById('article_form');
  let days = frm.elements['repeat_days'].value;
  for (let i = 1; i <= 7; i++) {
    if ((days & (1 << (i-1))) != 0)
      document.getElementById('d' + i).classList.add('selected');
  }
  checkDaysVisible();
}

function getDays() {
  let days = 0;
  for (let i = 1; i <= 7; i++) {
    if (document.getElementById('d' + i).classList.contains('selected'))
      days += (1 << (i-1));
  }
  return days;
}

function clickDay(_num) {
  let day = document.getElementById('d' + _num);
  day.classList.toggle('selected');
  let frm = document.getElementById('article_form');
  let days = getDays();
  frm.elements['repeat_days'].value = days;
  setRepeat();
}

function checkDaysVisible() {
  if (document.getElementById("id_repeat").selectedIndex == 2)
    document.getElementById("id_repeat_options_week").style.display = "flex";
  else
    document.getElementById("id_repeat_options_week").style.display = "none";
}

//-----------------------------------------------------------------
// Apps

function toggleApp(app) {
}

//-----------------------------------------------------------------
// Steps

function createStep(step_id, step_name) {
      img1 = document.createElement('img');
      img1.setAttribute('src', '/static/todo/icon/step-uncomplete.png');

      btn1 = document.createElement('button');
      btn1.setAttribute('type', 'button');
      btn1.setAttribute('onclick', 'stepComplete(' + step_id + ')');
      btn1.classList.add('field-icon');
      btn1.appendChild(img1);

      inp1 = document.createElement('input');
      inp1.setAttribute('type', 'text');
      inp1.setAttribute('id', 'step_' + step_id);
      inp1.setAttribute('onchange', 'stepChange(' + step_id + ')');
      inp1.setAttribute('value', step_name);
      inp1.setAttribute('maxlength', '200');
      inp1.setAttribute('required', '');
      
      div1 = document.createElement('div');
      div1.classList.add('editable-content');
      div1.classList.add('full-width');
      div1.classList.add('auxiliary-element');
      div1.appendChild(inp1);
      
      div2 = document.createElement('div');
      div2.classList.add('step-name');
      div2.appendChild(div1);

      img2 = document.createElement('img');
      img2.setAttribute('src', '/static/rok/icon/delete.png');

      btn2 = document.createElement('button');
      btn2.setAttribute('type', 'button');
      btn2.setAttribute('onclick', 'stepDelete(' + step_id + ')');
      btn2.classList.add('field-icon');
      btn2.appendChild(img2);
      
      div3 = document.createElement('div');
      div3.setAttribute('id', 'step_field_group_' + step_id);
      div3.classList.add('step-field-group');
      div3.appendChild(btn1);
      div3.appendChild(div2);
      div3.appendChild(btn2);

      div4 = document.getElementById('step_list');
      div4.appendChild(div3);
      
      inp1.focus();
}

function stepAdd() {
  x = document.getElementById('id_add_step');
  let name = x.value;
  x.value = '';

  let x = document.getElementsByName("csrfmiddlewaretoken");
  crsf = x[0].value; 

  let xhttp = new XMLHttpRequest();
  let url = step_api + "?" + postfix;
  xhttp.open("POST", url, true);
  xhttp.setRequestHeader('X-CSRFToken', crsf);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 201) {
      step_id = JSON.parse(this.responseText).id;
      step_name = JSON.parse(this.responseText).name;
      createStep(step_id, step_name);
    }
  };

  let data = "task=" + task_api + getItemId() + "/&name=" + encodeURI(name);
  xhttp.send(data);
}

function stepChange(id) {
  let task = task_api + getItemId();
  let x = document.getElementById('step_' + id);
  let name = x.value;
  let completed = x.classList.contains("completed");
  let data = "task=" + task + "/&name=" + encodeURI(name) + "&completed=" + completed;

  x = document.getElementsByName("csrfmiddlewaretoken");
  crsf = x[0].value; 

  let xhttp = new XMLHttpRequest();
  let url = step_api + id + "/?" + postfix;
  xhttp.open("PUT", url, true);
  xhttp.setRequestHeader('X-CSRFToken', crsf);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 201) {
    }
  };

  xhttp.send(data);
}

function stepComplete(id) {
  let y = document.getElementById('step_field_group_' + id);
  let x = document.getElementById('step_' + id);
  x.classList.toggle("completed");
  if (x.classList.contains("completed")) {
    y.childNodes[1].childNodes[1].setAttribute('src', '/static/todo/icon/step-complete.png');
  } else {
    y.childNodes[1].childNodes[1].setAttribute('src', '/static/todo/icon/step-uncomplete.png');
  }
  stepChange(id);
}

function stepDelete(id) {
  let x = document.getElementsByName("csrfmiddlewaretoken");
  crsf = x[0].value; 

  let xhttp = new XMLHttpRequest();
  xhttp.open("DELETE", step_api + id + "/", true);
  xhttp.setRequestHeader('X-CSRFToken', crsf);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      x = document.getElementById('step_field_group_' + id);
      x.classList.add('w3-hide');
    }
  };

  xhttp.send();
}



