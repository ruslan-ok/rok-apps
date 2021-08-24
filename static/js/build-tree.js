let tree_data = [], map = {};

function buildTree(tree_id, app, current_id) {
  let i, roots = [], node = {};

  let ul = document.getElementById(tree_id);
  if (!ul)
    return;
    
  for (let i = 0; i < ul.children.length; i++) {
    let li = ul.children[i];
    let id = li.dataset.id;
    tree_data.push({});
    tree_data[i].id = id;
    if (ul.children[i].dataset.parent)
      tree_data[i].parent = ul.children[i].dataset.parent;
    else
      tree_data[i].parent = '0';
    tree_data[i].children = [];
    tree_data[i].is_open = getOpen(id);
    tree_data[i].is_leaf = true;
    map[id] = i;
  }
  
  for (i = 0; i < tree_data.length; i += 1) {
    node = tree_data[i];
    if (node.parent !== '0') {
      tree_data[map[node.parent]].children.push(node);
      tree_data[map[node.parent]].is_leaf = false;
    } else {
      roots.push(node);
    }
  }

  for (let i = 0; i < roots.length; i++)
    initLi(roots[i], true);
}

function initLi(node, visible) {
  let li = document.getElementById('task_group_' + node.id);
  if (visible)
    li.classList.remove('hide');
  else
    li.classList.add('hide');

  if (!node.is_leaf)
    if (node.is_open)
      li.children[1].children[0].setAttribute('src', '/static/icon/groups/chevron-down.svg');
    else
      li.children[1].children[0].setAttribute('src', '/static/icon/groups/chevron-left.svg');

  for (let i = 0; i < node.children.length; i++)
    initLi(node.children[i], visible && node.is_open);
}

function toggleGroup(group_id) {
  let node = tree_data[map[group_id]];
  node.is_open = !node.is_open;
  setOpen(group_id, node.is_open);
  let li = document.getElementById('task_group_' + group_id);
  if (node.is_open)
    li.children[1].children[0].setAttribute('src', '/static/icon/groups/chevron-down.svg');
  else
    li.children[1].children[0].setAttribute('src', '/static/icon/groups/chevron-left.svg');
  let i;
  for (i = 0; i < node.children.length; i += 1)
    toggleLi(node.children[i].id, node.is_open);
}

function toggleLi(group_id, visible) {
  let li = document.getElementById('task_group_' + group_id);
  if (visible)
    li.classList.remove('hide');
  else
    li.classList.add('hide');
  let i, node = tree_data[map[group_id]];
  if (!node.is_leaf && node.is_open)
    for (i = 0; i < node.children.length; i += 1)
      toggleLi(node.children[i].id, visible);
}

function getOpen(group_id) {
  let name = 'grp_' + group_id;
  let value = localStorage.getItem(name);
  if (value == 'true')
    return true;
  return false;
}

function setOpen(group_id, value) {
  let name = 'grp_' + group_id;
  localStorage.setItem(name, value);
}


