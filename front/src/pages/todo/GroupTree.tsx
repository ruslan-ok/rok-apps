import type { MouseEvent } from 'react'
import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from '../../API'
import { IPageConfig } from '../PageConfig';


interface GroupItem {
    id: number;
    node_id: number;
    name: string;
    act_items_qty: number;
};

type Node = {
    id: number;
    node_id: number | null;
    children: number[];
    is_leaf: boolean;
    is_open: boolean | null;
    level: number;
    name: string;
    act_items_qty: number;
};

function getOpen(group_id: number) {
    let name = 'grp_' + group_id;
    let value = localStorage.getItem(name);
    if (value === 'true' || value === '1')
        return true;
    return false;
}
  
function setOpen(group_id: number, value: string) {
    let name = 'grp_' + group_id;
    localStorage.setItem(name, value);
}

function toggleClasses(element: HTMLElement, condition: boolean, ifTrue: string, ifFalse: string) {
    if (condition) {
        element.classList.add(ifTrue);
        element.classList.remove(ifFalse);
    } else {
        element.classList.add(ifFalse);
        element.classList.remove(ifTrue);
    }
}

function toggleLi(group_id: number, visible: boolean) {
    let li = document.getElementById('task_group_' + group_id);
    if (li) {
        if (visible) {
            li.classList.add('d-flex');
            li.classList.remove('d-none');
        } else {
            li.classList.add('d-none');
            li.classList.remove('d-flex');
        }
        const node = getNodeById(group_id);
        if (node && !node.is_leaf && node.is_open) {
            for (const child_id of node.children) {
                toggleLi(child_id, visible);
            }
        }
    }
}

function handleClick(event: MouseEvent<HTMLElement>) {
    let el: HTMLElement = event.target;
    while (el.tagName !== 'BUTTON' && el.parentElement) {
        el = el.parentElement;
    }
    const group_id = +el.dataset.id;
    const node = getNodeById(group_id);
    if (node) {
        node.is_open = !node.is_open;
        setOpen(group_id, node.is_open ? '1' : '0');
        toggleClasses(el.children[0].children[0], node.is_open, 'bi-folder2-open', 'bi-folder2');
        toggleClasses(el.children[1], node.is_open, 'bi-chevron-down', 'bi-chevron-left');
        for (const child_id of node.children) {
            toggleLi(child_id, node.is_open);
        }
    }
}

let nodes: Node[];

function getNodeById(id: number): Node | null {
    return nodes.find(x => x.id === id) || null;
}

function allNodesAreOpen(id: number): boolean {
    let ret = true;
    let node = getNodeById(id);
    while (node && node.node_id) {
        const parent = getNodeById(node.node_id);
        if (parent) {
            if (!parent.is_open) {
                ret = false;
                break;
            }
            node = parent;
        } else {
            break;
        }
    }
    return ret;
}

function getItemById(items: GroupItem[], id: number): GroupItem | null {
    return items.find(x => x.id === id) || null;
}

function addNode(items: GroupItem[], item: GroupItem): Node {
    let node = getNodeById(item.id);
    if (node)
        return node;
    node = {
        id: item.id,
        name: item.name,
        node_id: item.node_id,
        act_items_qty: item.act_items_qty,
        children: [],
        is_leaf: true,
        is_open: null,
        level: 0,
    };
    nodes.push(node);
    if (node.node_id) {
        let parent = getNodeById(node.node_id);
        if (!parent) {
            const parentItem: GroupItem | null = getItemById(items, node.node_id);
            if (parentItem)
                parent = addNode(items, parentItem);
        }
        if (parent) {
            parent.is_leaf = false;
            parent.children.push(node.id);
            node.level = parent.level + 1;
            if (parent.is_open === null) {
                parent.is_open = getOpen(parent.id);
            }
        }
    }
    return node;
}

function hierToFlat(root: number[]): Array<number> {
    let ret: number[] = [];
    function compare(a: number, b: number): number {
        const oa = getNodeById(a);
        const ob = getNodeById(b);
        if (!oa || !ob)
            return 0;
        if (oa.name < ob.name){
            return -1;
        }
        if (oa.name > ob.name){
            return 1;
        }
        return 0;
    }
    const sortedRoot = root.sort(compare);
    sortedRoot.forEach(x => {
        ret.push(x);
        const node = getNodeById(x);
        if (node && node.children.length) {
            const cld = hierToFlat(node.children);
            ret = ret.concat(cld);
        }
    });
    return ret;
}

function GroupTree({config}: {config: IPageConfig}) {
    const [items, setData] = useState<GroupItem[]>([]);
    useEffect(() => {
        const getData = async () => {
          const items: GroupItem[] = await api.get('group', {app: config.view_group.app, role: config.view_group.role});
          setData(items);
        };
      
        getData();
    }, [config]);

    let groups = <></>;

    if (items.length) {
        nodes = [];
        items.forEach(item => {
            addNode(items, item);
        });
        const root: number[] = nodes.filter(x => !x.node_id).map(x => x.id);
        const flat = hierToFlat(root);
        const groupList = flat.map((id) => {
            const group = getNodeById(id);
            if (!group)
                return <></>;
            let itemLink;
            const g_id = `task_group_${group.id}`;
            const is_visible = allNodesAreOpen(group.id);
            const active = (group.id === config.entity.id);
            const gclass = is_visible ? 'd-flex' + (active ? ' active' : '') : ' d-none';
            const bgColor = active ? 'lightgrey' : 'white';
            const elStyle = {
                padding: '2px 6px',
                textDecoration: 'none',
                border: 'none',
                borderRadius: '4px',
                backgroundColor: bgColor,
                margin: '0',
                color: 'var(--bs-secondary-text-emphasis)',
                justifyContent: 'space-between',
                width: '100%',
            };

            if (group.is_leaf) {
                const href = `/${config.view_group.app}/?${config.entity.name}=${group.id}`;
                const item_class = `me-2 bi-journals level-${group.level}`;
                itemLink = (
                    <Link id={g_id} key={group.id} to={href} data-id={group.id} data-parent={group.node_id} className={gclass} aria-current={active} style={elStyle} >
                        <div>
                            <i className={item_class}></i>
                            <span className="">{group.name}</span>
                        </div>
                        <span>{group.act_items_qty}</span>
                    </Link>
                );
            } else {
                const folder_class = `me-2 bi-folder2${group.is_open ? '-open' : ''} level-${group.level}`;
                const chevron_class = `bi-chevron-${group.is_open ? 'down' : 'left'}`;
                itemLink = (
                    <button id={g_id} key={group.id} data-id={group.id} data-parent={group.node_id} className={gclass} onClick={handleClick} style={elStyle} >
                        <div>
                            <i className={folder_class}></i>
                            <span className="">{group.name}</span>
                        </div>
                        <i className={chevron_class}></i>
                    </button>
                );
            }

            return itemLink;
        });

        groups = <div id="groups-tree" className="rok-group-tree">{groupList}</div>;
    }

    return groups;
}
    
export default GroupTree;