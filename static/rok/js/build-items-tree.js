
var grp_list = [], grp_map = {}, itm_list = [], itm_map = {};

function build_items_tree(tree_id, context) {
  var i, grp_num = 0, itm_num = 0;

  var tree = document.getElementById(tree_id);
  for (var i = 0; i < tree.children.length; i++) {
    var div = tree.children[i];
    var id = div.dataset.grp_id;
    if (id) {
      grp_list.push({});
      grp_list[grp_num].id = id;
      grp_list[grp_num].is_open = get_open(context, id);
      grp_map[id] = grp_num;
      grp_num += 1;
    }
    id = div.dataset.itm_id;
    if (id && (id > 0)) {
      itm_list.push({});
      itm_list[itm_num].grp_id = id;
      itm_list[itm_num].visible = grp_list[grp_map[id]].is_open;
      itm_map[id] = itm_num;
      itm_num += 1;
    }
  }
  
  for (var i = 0; i < grp_list.length; i++)
    init_grp(grp_list[i]);
  
  for (var i = 0; i < itm_list.length; i++)
    init_itm(itm_list[i]);
}

function init_grp(grp) {
  var div = document.getElementById('grp_' + grp.id);
  if (grp.is_open)
    div.children[0].children[0].setAttribute('src', '/static/rok/icon/direct-down.png');
  else
    div.children[0].children[0].setAttribute('src', '/static/rok/icon/direct-right.png');
}

function init_itm(itm) {
  var div = document.getElementById('itm_' + itm.grp_id);
  if (itm.visible)
    div.classList.remove('hide');
  else
    div.classList.add('hide');
}

function toggle_items_group(context, group_id) {
  var grp = grp_list[grp_map[group_id]];
  grp.is_open = !grp.is_open;
  set_open(context, group_id, grp.is_open);
  init_grp(grp);
  var itm = itm_list[itm_map[group_id]];
  itm.visible = grp.is_open;
  init_itm(itm);
}

function get_open(context, group_id) {
  var name = context + '_grp_' + group_id;
  var value = localStorage.getItem(name);
  if (value == 'true')
    return true;
  return false;
}

function set_open(context, group_id, value) {
  var name = context + '_grp_' + group_id;
  localStorage.setItem(name, value);
}


