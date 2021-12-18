var protectedValue = true;
valueEditCheck();

function valueEditCheck()
{
  element = document.getElementById('id_value');
  var generator = !protectedValue || (element.value == '')
  element.readOnly = !generator;
  if (generator)
  {
    if (element.value != '')
      document.getElementById('id_ln').value = element.value.length;
    else
      document.getElementById('id_ln').value = document.getElementById('id_default_len').value;

    var params = document.getElementById('id_params').value;
    if (params == 0)
      params = document.getElementById('id_default_params').value;
    document.getElementById('id_uc').checked = (params & 1);
    document.getElementById('id_lc').checked = (params & 2);
    document.getElementById('id_dg').checked = (params & 4);
    document.getElementById('id_sp').checked = (params & 8);
    document.getElementById('id_br').checked = (params & 16);
    document.getElementById('id_mi').checked = (params & 32);
    document.getElementById('id_ul').checked = (params & 64);
    document.getElementById('id_ac').checked = (params & 128);
  }
  document.getElementById('id_edit').classList.toggle('d-none');
  document.getElementById('id_execute').classList.toggle('d-none');
  document.getElementById('id_options').classList.toggle('d-none');
  document.getElementById('id_buttons').classList.toggle('d-none');
}

function openParams()
{
  protectedValue = false;
  valueEditCheck();
}

function closeParams()
{
  protectedValue = true;
  valueEditCheck();
}

function buildValue()
{
  var ln = document.getElementById('id_ln').value;
  var uc = document.getElementById('id_uc').checked;
  var lc = document.getElementById('id_lc').checked;
  var dg = document.getElementById('id_dg').checked;
  var sp = document.getElementById('id_sp').checked;
  var br = document.getElementById('id_br').checked;
  var mi = document.getElementById('id_mi').checked;
  var ul = document.getElementById('id_ul').checked;
  var ac = document.getElementById('id_ac').checked;

  var allowed_chars = '';

  if (uc)
  {
    allowed_chars += 'ABCDEFGHJKLMNPQRSTUVWXYZ';
    if (!ac)
        allowed_chars += 'IO';
  }

  if (lc)
  {
    allowed_chars += 'abcdefghjkmnpqrstuvwxyz';
    if (!ac)
        allowed_chars += 'io';
  }

  if (dg)
  {
    allowed_chars += '23456789';
    if (!ac)
        allowed_chars += '10';
  }

  if (sp)
    allowed_chars += '!@#$%^&*=+';

  if (br)
    allowed_chars += '()[]{}<>';

  if (mi)
    allowed_chars += '-';

  if (ul)
    allowed_chars += '_';

  if (allowed_chars == '')
    allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*(-_=+)';

  var randomString = '';
  for (var i = 0; i < ln; i++)
  {
    var randomPoz = Math.floor(Math.random() * allowed_chars.length);
    randomString += allowed_chars.substring(randomPoz, randomPoz + 1);
  }
  document.getElementById('id_value').value = randomString;

  var params = 0;
  if (uc)
    params += 1;
  if (lc)
    params += 2;
  if (dg)
    params += 4;
  if (sp)
    params += 8;
  if (br)
    params += 16;
  if (mi)
    params += 32;
  if (ul)
    params += 64;
  if (ac)
    params += 128;

  document.getElementById('id_params').value = params;
  document.getElementById('id_item_save').click();
}

function copyToClipboard(fld, kind) {
    const value = fld.parentNode.parentNode.children[0].value;
    if (!navigator.clipboard) {
        fallbackCopyTextToClipboard(value);
        return;
      }
      navigator.clipboard.writeText(value).then(function() {
        alert(kind, 'Copied to clipboard.', 'success');
      }, function(err) {
        alert(kind, 'Could not copy text: ' + err, 'danger');
      });
}

function alert(kind, message, type) {
    const alertPlaceholder = document.getElementById(kind + 'AlertPlaceholder');
    const wrapper = document.createElement('div');
    wrapper.innerHTML = '<div class="alert alert-' + type + ' alert-dismissible" role="alert">' + message + '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>';
    alertPlaceholder.append(wrapper);
}
