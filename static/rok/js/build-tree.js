
var tree_data = [], map = {};

function build_tree(tree_id, app, current_id) {
  var i, roots = [], node = {};

  var ul = document.getElementById(tree_id);
  for (var i = 0; i < ul.children.length; i++) {
    var li = ul.children[i];
    var id = li.dataset.id;
    tree_data.push({});
    tree_data[i].id = id;
    if (ul.children[i].dataset.parent)
      tree_data[i].parent = ul.children[i].dataset.parent;
    else
      tree_data[i].parent = '0';
    tree_data[i].children = [];
    tree_data[i].is_open = get_open(id);
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

  for (var i = 0; i < roots.length; i++)
    init_li(roots[i], true);
}

function init_li(node, visible) {
  var li = document.getElementById('task_group_' + node.id);
  if (visible)
    li.classList.remove('hide');
  else
    li.classList.add('hide');

  if (!node.is_leaf)
    if (node.is_open)
      li.children[1].children[0].setAttribute('src', '/static/rok/icon/direct-down.png');
    else
      li.children[1].children[0].setAttribute('src', '/static/rok/icon/direct-left.png');

  for (var i = 0; i < node.children.length; i++)
    init_li(node.children[i], visible && node.is_open);
}

function toggle_group(group_id) {
  var node = tree_data[map[group_id]];
  node.is_open = !node.is_open;
  set_open(group_id, node.is_open);
  var li = document.getElementById('task_group_' + group_id);
  if (node.is_open)
    li.children[1].children[0].setAttribute('src', '/static/rok/icon/direct-down.png');
  else
    li.children[1].children[0].setAttribute('src', '/static/rok/icon/direct-left.png');
  var i;
  for (i = 0; i < node.children.length; i += 1)
    toggle_li(node.children[i].id, node.is_open);
}

function toggle_li(group_id, visible) {
  var li = document.getElementById('task_group_' + group_id);
  if (visible)
    li.classList.remove('hide');
  else
    li.classList.add('hide');
  var i, node = tree_data[map[group_id]];
  if (!node.is_leaf && node.is_open)
    for (i = 0; i < node.children.length; i += 1)
      toggle_li(node.children[i].id, visible);
}

function get_open(group_id) {
  var name = 'grp_' + group_id;
  var value = localStorage.getItem(name);
  if (value == 'true')
    return true;
  return false;
}

function set_open(group_id, value) {
  var name = 'grp_' + group_id;
  localStorage.setItem(name, value);
}


