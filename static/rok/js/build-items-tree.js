
let grp_list = [], grp_map = {}, itm_list = [], itm_map = {};

function buildItemsTree(tree_id, context) {
  let i, grp_num = 0, itm_num = 0;

  let tree = document.getElementById(tree_id);
  for (let i = 0; i < tree.children.length; i++) {
    let div = tree.children[i];
    let id = div.dataset.grp_id;
    if (id) {
      grp_list.push({});
      grp_list[grp_num].id = id;
      grp_list[grp_num].is_open = getGroupOpen(context, id);
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
  
  for (let i = 0; i < grp_list.length; i++)
    initGroup(grp_list[i]);
  
  for (let i = 0; i < itm_list.length; i++)
    initItem(itm_list[i]);
}

function initGroup(grp) {
  let div = document.getElementById('grp_' + grp.id);
  if (grp.is_open)
    div.children[0].children[0].setAttribute('src', '/static/rok/icon/direct-down.png');
  else
    div.children[0].children[0].setAttribute('src', '/static/rok/icon/direct-right.png');
}

function initItem(itm) {
  let div = document.getElementById('itm_' + itm.grp_id);
  if (itm.visible)
    div.classList.remove('hide');
  else
    div.classList.add('hide');
}

function toggleItemsGroup(context, group_id) {
  let grp = grp_list[grp_map[group_id]];
  grp.is_open = !grp.is_open;
  setGroupOpen(context, group_id, grp.is_open);
  initGroup(grp);
  let itm = itm_list[itm_map[group_id]];
  itm.visible = grp.is_open;
  initItem(itm);
}

function getGroupOpen(context, group_id) {
  let name = context + '_grp_' + group_id;
  let value = localStorage.getItem(name);
  if (value == 'true')
    return true;
  return false;
}

function setGroupOpen(context, group_id, value) {
  let name = context + '_grp_' + group_id;
  localStorage.setItem(name, value);
}


