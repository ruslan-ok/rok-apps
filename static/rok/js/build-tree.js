
var tree_data, map = {};

function build_tree(tree_id, app, current_id) {
  var request = new XMLHttpRequest();
  var requestURL = 'http://localhost:8000/ru/groups.json';
  var url = requestURL;
  if (app)
    url = requestURL + '?app=' + app;
  request.open('GET', url);
  request.responseType = 'json';
  request.send();
  request.onload = function() {
    tree_data = request.response;
    parse_groups(tree_id, current_id);
  }
}

function parse_groups(tree_id, current_id) {
  var i, roots = [], node;
  for (i = 0; i < tree_data.length; i += 1) {
    map[tree_data[i].id] = i;
    tree_data[i].is_open = get_open(tree_data[i].id);
    tree_data[i].is_leaf = true;
    tree_data[i].children = [];
  }
  
  for (i = 0; i < tree_data.length; i += 1) {
    node = tree_data[i];
    if (node.node !== null) {
      tree_data[map[node.node]].children.push(node);
      tree_data[map[node.node]].is_leaf = false;
    } else {
      roots.push(node);
    }
  }
  
  var ul = document.getElementById(tree_id);
  for (i = 0; i < roots.length; i += 1)
    add_li(ul, tree_data[map[roots[i].id]], current_id, 0, true);
}

function add_li(ul, data, current_id, level, visible) {
  var li = document.createElement('li');
  li.classList.add('grp-item');
  if (!visible)
    li.classList.add('hide');
  li.setAttribute('id', 'task_group_' + data.id);
  if (current_id == data.id)
      li.classList.add('selected');
  var a1 = document.createElement('a');
  a1.setAttribute('href', 'list/' + data.id + '/');
  var div1 = document.createElement('div');
  div1.classList.add('nav-menu-item-left');
  var img1 = document.createElement('img');
  img1.classList.add('level-' + level);
  if (data.is_leaf)
    img1.setAttribute('src', '/static/rok/icon/list.png');
  else
    img1.setAttribute('src', '/static/rok/icon/group.png');
  div1.appendChild(img1);
  var div2 = document.createElement('div');
  div2.innerHTML = data.name;
  div1.appendChild(div2);
  a1.appendChild(div1);
  li.appendChild(a1);
  var div3 = document.createElement('div');
  if (data.is_leaf) {
    div3.classList.add('nav-menu-qty');
    div3.innerHTML = '0';
  }
  else {
    div3.classList.add('nav-menu-item-right');
    div3.setAttribute('onclick','toggle_group(' + data.id + ')')
    //var a2 = document.createElement('a');
    //a2.setAttribute('href', '#');
    var img2 = document.createElement('img');
    img2.classList.add('img-20_20');
    if (data.is_open)
      img2.setAttribute('src', '/static/rok/icon/direct-down.png');
    else
      img2.setAttribute('src', '/static/rok/icon/direct-left.png');
    //a2.appendChild(img2);
    //div3.appendChild(a2);
    div3.appendChild(img2);
  }
  li.appendChild(div3);
  ul.appendChild(li);
  var i;
  for (i = 0; i < data.children.length; i += 1)
    add_li(ul, data.children[i], current_id, level + 1, visible && data.is_open);
}

function toggle_group(group_id) {
  var data = tree_data[map[group_id]];
  data.is_open = !data.is_open;
  set_open(group_id, data.is_open);
  var li = document.getElementById('task_group_' + group_id);
  if (data.is_open)
    li.children[1].children[0].setAttribute('src', '/static/rok/icon/direct-down.png');
  else
    li.children[1].children[0].setAttribute('src', '/static/rok/icon/direct-left.png');
  var i;
  for (i = 0; i < data.children.length; i += 1)
    toggle_li(data.children[i].id, data.is_open);
}

function toggle_li(group_id, visible) {
  var li = document.getElementById('task_group_' + group_id);
  if (visible)
    li.classList.remove('hide');
  else
    li.classList.add('hide');
  var i, data = tree_data[map[group_id]];
  if (!data.is_leaf && data.is_open)
    for (i = 0; i < data.children.length; i += 1)
      toggle_li(data.children[i].id, visible);
}

function get_open(group_id) {
  var name = 'grp_' + group_id + '=';
  var ca = document.cookie.split(';');
  for(var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return (c.substring(name.length, c.length) == '1');
    }
  }
  return false;
}

function set_open(group_id, value) {
  var c = 'grp_' + group_id + '=';
  if (value)
    c += '1;';
  else
    c += '0;';
  document.cookie = c;
}

