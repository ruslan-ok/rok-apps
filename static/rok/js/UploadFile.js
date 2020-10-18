function UploadFile()
{
  document.getElementById('id_upload').click();
}

function FileSelected()
{
  document.getElementById('loadFile').innerText = document.getElementById('id_upload').files[0].name;
  document.getElementById('id_submit').click();
}
