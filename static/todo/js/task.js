const host_api = "http://localhost:8000/api/tasks/";
const postfix = "/?format=json";

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
  var sel_id = name + '-select';
  if (document.getElementById(sel_id).style.display == "none")
    document.getElementById(sel_id).style.display = "block";
  else
    document.getElementById(sel_id).style.display = "none";
}

function afterCalendarChanged(init, field) {
  if ((field == 1) || (field == 0)) {
    var dt = document.getElementById("id_remind_0");
    var tm = document.getElementById("id_remind_1");
    setRemind(dt.value, tm.value);
  }
  if ((field == 2) || (field == 0)) {
    var dt = document.getElementById("id_stop_0");
    var tm = document.getElementById("id_stop_1");
    setTermin(dt.value, tm.value);
  }
}

//-----------------------------------------------------------------
// Completed

function toggleCompleted() {
  var x = document.getElementById("task-completed");
  if (x.dataset.value.toLowerCase() == "true")
    x.dataset.value = "false";
  else
    x.dataset.value = "true";

  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", host_api + getItemId() + "/completed" + postfix, true);

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
  var x = document.getElementById("task-important");
  if (x.dataset.value.toLowerCase() == "true")
    x.dataset.value = "false";
  else
    x.dataset.value = "true";

  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", host_api + getItemId() + "/important" + postfix, true);

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
  var x = document.getElementById("myday");
  var value = x.classList.contains("selected");
  x.classList.toggle("selected");
  
  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", host_api + getItemId() + "/in_my_day" + postfix, true);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      x.innerHTML = JSON.parse(this.responseText).title;
    }
  };

  xhttp.send();
}

//-----------------------------------------------------------------
// Remind and Termin common

function changeDateTime(mode, entity) {
  var x = document.getElementById(entity + "-view");
  var y = x.childNodes[1].childNodes[1].childNodes[3].childNodes[1];

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

  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", host_api + getItemId() + "/" + func + postfix, true);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      y.childNodes[1].innerHTML = JSON.parse(this.responseText).date;
      y.childNodes[3].innerHTML = JSON.parse(this.responseText).time;
    }
  };

  xhttp.send();
}

function setDateTime(dt, tm, entity) {
  var x = document.getElementById(entity + "-view");
  var y = x.childNodes[1].childNodes[1].childNodes[3].childNodes[1];

  y.childNodes[1].classList.add("actual");
  x.childNodes[1].childNodes[3].classList.remove("hide");

  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", host_api + getItemId() + "/" + entity + "_set/" + dt + "/" + tm + postfix, true);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      y.childNodes[1].innerHTML = JSON.parse(this.responseText).date;
      y.childNodes[3].innerHTML = JSON.parse(this.responseText).time;
    }
  };

  xhttp.send();
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
// Termin

function changeTermin(mode) {
  changeDateTime(mode, "termin");
}

function setTermin(dt, tm) {
  setDateTime(dt, tm, "termin")
}

//-----------------------------------------------------------------
// Repeat

function changeRepeat(_repeat, _workdays) {
  var ndx;
  switch(_repeat) {
    case 0: ndx = 0; break;
    case 1: ndx = 1; break;
    case 3: ndx = 2; break;
    case 4: ndx = 3; break;
    case 5: ndx = 4; break;
    default: ndx = 0;
  }
  
  if (_workdays) {
    var frm = document.getElementById('article_form');
    frm.elements['repeat_days'].value = 31;
    initDays();
  }

  document.getElementById("id_repeat").selectedIndex = ndx;

  checkDaysVisible();
}

//-----------------------------------------------------------------
// Repeat Days

function initDays() {
  var frm = document.getElementById('article_form');
  var days = frm.elements['repeat_days'].value;
  for (var i = 1; i <= 7; i++) {
    if ((days & (1 << (i-1))) != 0)
      document.getElementById('d' + i).classList.add('selected');
  }
  checkDaysVisible();
}

function getDays() {
  var days = 0;
  for (var i = 1; i <= 7; i++) {
    if (document.getElementById('d' + i).classList.contains('selected'))
      days += (1 << (i-1));
  }
  return days;
}

function clickDay(_num) {
  var day = document.getElementById('d' + _num);
  day.classList.toggle('selected');
  var frm = document.getElementById('article_form');
  var days = getDays();
  frm.elements['repeat_days'].value = days;
}

function checkDaysVisible() {
  if (document.getElementById("id_repeat").selectedIndex == 2)
    document.getElementById("id_repeat_options_week").style.display = "flex";
  else
    document.getElementById("id_repeat_options_week").style.display = "none";
}

