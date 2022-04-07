document.getElementById('remind-select').style.display = "none";
document.getElementById('termin-select').style.display = "none";
document.getElementById('repeat-select').style.display = "none";
initDays();

function toggleSelectField(name)
{
  var sel_id = name + '-select';
  if (document.getElementById(sel_id).style.display == "none")
    document.getElementById(sel_id).style.display = "block";
  else
    document.getElementById(sel_id).style.display = "none";
}

//-----------------------------------------------------------------
// Repeat Days

function initDays()
{
  var frm = document.getElementById('article_form');
  var days = frm.elements['repeat_days'].value;
  for (var i = 1; i <= 7; i++)
  {
    if ((days & (1 << (i-1))) != 0)
      document.getElementById('d' + i).classList.add('selected');
  }
}

function getDays()
{
  var days = 0;
  for (var i = 1; i <= 7; i++)
  {
    if (document.getElementById('d' + i).classList.contains('selected'))
      days += (1 << (i-1));
  }
  return days;
}

function dayClick(_num)
{
  var day = document.getElementById('d' + _num);
  day.classList.toggle('selected');
  var frm = document.getElementById('article_form');
  var days = getDays();
  frm.elements['repeat_days'].value = days;
}
