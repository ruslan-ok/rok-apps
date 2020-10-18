document.getElementById('remind-select').style.display = "none";
document.getElementById('termin-select').style.display = "none";
document.getElementById('repeat-select').style.display = "none";
InitDays();

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
  var frm = document.getElementById('task_form');
  var days = frm.elements['repeat_days'].value;
  for (var i = 1; i <= 7; i++)
  {
    if ((days & (1 << (i-1))) != 0)
      document.getElementById('d' + i).classList.add('selected');
  }
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
  var frm = document.getElementById('task_form');
  var days = GetDays();
  frm.elements['repeat_days'].value = days;
}
