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

function toggleClasses(element, condition, ifTrue, ifFalse) {
  if (condition) {
    element.classList.add(ifTrue);
    element.classList.remove(ifFalse);
  } else {
    element.classList.add(ifFalse);
    element.classList.remove(ifTrue);
  }
}

function initLi(node, visible) {
  let li = document.getElementById('task_group_' + node.id);
  toggleClasses(li, visible, 'sidebar__group-visible', 'sidebar__group-hidden');

  if (!node.is_leaf) {
    toggleClasses(li.children[0].children[0], node.is_open, 'bi-folder2-open', 'bi-folder2');
    toggleClasses(li.children[1], node.is_open, 'bi-chevron-down', 'bi-chevron-left');
  }
  for (let i = 0; i < node.children.length; i++)
    initLi(node.children[i], visible && node.is_open);
}

function toggleGroup(group_id) {
  let node = tree_data[map[group_id]];
  node.is_open = !node.is_open;
  setOpen(group_id, node.is_open);
  let li = document.getElementById('task_group_' + group_id);
  toggleClasses(li.children[0].children[0], node.is_open, 'bi-folder2-open', 'bi-folder2');
  toggleClasses(li.children[1], node.is_open, 'bi-chevron-down', 'bi-chevron-left');
  let i;
  for (i = 0; i < node.children.length; i += 1)
    toggleLi(node.children[i].id, node.is_open);
}

function toggleLi(group_id, visible) {
  let li = document.getElementById('task_group_' + group_id);
  if (visible) {
    li.classList.add('sidebar__group-visible');
    li.classList.remove('sidebar__group-hidden');
  } else {
    li.classList.add('sidebar__group-hidden');
    li.classList.remove('sidebar__group-visible');
  }
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


