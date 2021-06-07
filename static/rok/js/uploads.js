function uploadFile() {
  document.getElementById('id_upload').click();
}

function fileSelected() {
  filename = document.getElementById('id_upload').files[0].name;
  fn_element = document.getElementById('loadFile');
  if (fn_element)
    fn_element.innerText = filename;
  document.getElementById('id_submit').click();
}
