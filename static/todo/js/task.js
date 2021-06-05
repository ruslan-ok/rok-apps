const host_api = "http://localhost:8000/api/tasks/";
const postfix = "/?format=json";

document.getElementById('remind-select').style.display = "none";
document.getElementById('termin-select').style.display = "none";
document.getElementById('repeat-select').style.display = "none";
InitDays();

// Getting the id of the item being edited
function GetItemId() {
  return document.getElementById("article_form").dataset.item_id;
}

function ToggleSelectField(name)
{
  var sel_id = name + '-select';
  if (document.getElementById(sel_id).style.display == "none")
    document.getElementById(sel_id).style.display = "block";
  else
    document.getElementById(sel_id).style.display = "none";
}

function InitDays()
{
  var frm = document.getElementById('article_form');
  var days = frm.elements['repeat_days'].value;
  for (var i = 1; i <= 7; i++)
  {
    if ((days & (1 << (i-1))) != 0)
      document.getElementById('d' + i).classList.add('selected');
  }
  CheckDaysVisible();
}

function GetDays()
{
  var days = 0;
  for (var i = 1; i <= 7; i++)
  {
    if (document.getElementById('d' + i).classList.contains('selected'))
      days += (1 << (i-1));
  }
  return days;
}

function DayClick(_num)
{
  var day = document.getElementById('d' + _num);
  day.classList.toggle('selected');
  var frm = document.getElementById('article_form');
  var days = GetDays();
  frm.elements['repeat_days'].value = days;
}

function CheckDaysVisible()
{
  if (document.getElementById("id_repeat").selectedIndex == 2)
    document.getElementById("id_repeat_options_week").style.display = "flex";
  else
    document.getElementById("id_repeat_options_week").style.display = "none";
}

function SetRepeat(_repeat, _workdays)
{
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
    InitDays();
  }

  document.getElementById("id_repeat").selectedIndex = ndx;

  CheckDaysVisible();
}

function SetTermin(_mode) {
  var x = document.getElementById("id_stop");
  
  var _id = GetItemId();

  if (_mode == 0) {
    x.value = "";

    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", host_api + _id + "/termin_delete" + postfix, true);

    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
        x.innerHTML = JSON.parse(this.responseText).title;
      }
    };

    xhttp.send();

    SetRepeat(0);

    return;
  }
  
  date = new Date(Date.now());
  
  if (_mode == 2) {
    date.setDate(date.getDate() + 1);
  }
  
  if (_mode == 3) {
    var day = date.getDay();
    date.setDate(date.getDate() + (8 - day));
  }
  
  x.value = date.toISOString().substr(0, 10);
}

// Button "My day" click handling
function ToggleMyDay() {
  var x = document.getElementById("myday");
  var value = x.classList.contains("selected");
  x.classList.toggle("selected");
  
  var _id = GetItemId();

  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", host_api + _id + "/in_my_day" + postfix, true);

  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      x.innerHTML = JSON.parse(this.responseText).title;
    }
  };

  xhttp.send();
}

