let dir_list = [], dir_map = {};

function buildDirTree(tree_id) {
    let ul = document.getElementById(tree_id);
    if (!ul)
        return;
    
    let i;
    let id = 1;
    for (let i = 0; i < ul.children.length; i++) {
        let li = ul.children[i];
        li.setAttribute('id', 'id_dir_' + id);
        let x = {};
        x.id = id;
        x.name = li.dataset.name;
        x.active = li.classList.contains('active');
        let parent_id = 0;
        x.parent = li.dataset.parent;
        if (x.parent != '') {
            let p = x.parent;
            let c = dir_map[p];
            let d = dir_list[c];
            parent_id = d.id;
        }
        li.dataset.parent_id = parent_id.toString();
        x.parent_id = parent_id;
        x.children = [];
        x.is_open = getOpen(id);
        x.is_leaf = true;
        let parent = x.parent;
        if (parent.length > 0)
            parent += '/';
        dir_list.push(x);
        dir_map[parent + x.name] = i;
        id++;
    }
  
    let roots = [], node = {};
    for (i = 0; i < dir_list.length; i++) {
        node = dir_list[i];
        if (node.parent_id == 0)
            roots.push(node);
        else {
            let parent_node = dir_list[dir_map[node.parent]];
            parent_node.children.push(node);
            if (parent_node.is_leaf) {
                parent_node.is_leaf = false;
                let icon = document.getElementById('id_dir_' + parent_node.id).children[0].children[1];
                icon.setAttribute('onclick', 'toggleDir(' + parent_node.id + ')');
                icon.classList.remove('bi-dot');
                icon.classList.remove('invisible');
                icon.classList.add('bi-chevron-right');
            }
            if (node.active) {
                let parent_id = node.parent_id;
                while (parent_id) {
                    parent_node = dir_list.filter((x)=>(x.id==parent_id))[0];
                    if (!parent_node.is_open) {
                        parent_node.is_open = true;
                        setOpen(parent_node.id, true);
                        let j;
                        for (j = 0; j < parent_node.children.length; j++)
                            toggleLi(parent_node.children[j].id, true);
                    }
                    parent_id = parent_node.parent_id;
                }
            }
        }
    }

    for (let i = 0; i < roots.length; i++)
        initLi(roots[i], true);
}

function initLi(node, visible) {
    let li = document.getElementById('id_dir_' + node.id);
    toggleClasses(li, visible, 'visible', 'hidden');

    if (!node.is_leaf) {
        toggleClasses(li.children[0].children[1], node.is_open, 'bi-chevron-down', 'bi-chevron-right');
    }
    for (let i = 0; i < node.children.length; i++)
        initLi(node.children[i], visible && node.is_open);
}

function getOpen(dir_id) {
    let name = 'dir_' + dir_id;
    let value = localStorage.getItem(name);
    return (value == 'true');
}

function setOpen(dir_id, value) {
    let name = 'dir_' + dir_id;
    localStorage.setItem(name, value);
}
  
function toggleDir(dir_id) {
    let node = dir_list.filter((x)=>(x.id==dir_id))[0];
    node.is_open = !node.is_open;
    setOpen(dir_id, node.is_open);
    let li = document.getElementById('id_dir_' + dir_id);
    toggleClasses(li.children[0].children[1], node.is_open, 'bi-chevron-down', 'bi-chevron-right');
    let i;
    for (i = 0; i < node.children.length; i += 1)
        toggleLi(node.children[i].id, node.is_open);
}
  
function toggleLi(dir_id, visible) {
    let li = document.getElementById('id_dir_' + dir_id);
    if (visible) {
        li.classList.add('visible');
        li.classList.remove('hidden');
    } else {
        li.classList.add('hidden');
        li.classList.remove('visible');
    }
    let i, node = dir_list.filter((x)=>(x.id==dir_id))[0];
    if (!node.is_leaf && node.is_open)
        for (i = 0; i < node.children.length; i += 1)
            toggleLi(node.children[i].id, visible);
}
  
  