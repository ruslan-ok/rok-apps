export interface GroupItem {
    id: number;
    node_id: number;
    name: string;
    is_leaf: boolean;
    level: number;
    act_items_qty: number;
};

type Node = {
    id: number;
    node_id: number | null;
    children: number[];
    is_leaf: boolean;
    is_open: boolean | null;
    level: number;
};

function GroupTree({items, current, app, entity}: {items: GroupItem[], current: number | string | undefined, app: string, entity: string}) {

    let nodes: Node[] = [];

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
                li.classList.add('sidebar__group-visible');
                li.classList.remove('sidebar__group-hidden');
            } else {
                li.classList.add('sidebar__group-hidden');
                li.classList.remove('sidebar__group-visible');
            }
            const node = getNodeById(group_id);
            if (node && !node.is_leaf && node.is_open) {
                for (const child_id of node.children) {
                    toggleLi(child_id, visible);
                }
            }
        }
    }

    function handleClick(e) {
        let el = e.target;
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

    let groups = <></>;

    if (items.length) {
        const groupList = items.map((item) => {
            const group: Node = {
                'id': item.id,
                'node_id': item.node_id,
                'children': [],
                'is_leaf': item.is_leaf,
                'is_open': item.is_leaf ? null : getOpen(item.id),
                'level': item.level,
            };
            nodes.push(group);
            if (group.node_id) {
                const parent = getNodeById(group.node_id);
                if (parent) {
                    parent.children.push(group.id);
                }
            }

            let itemLink;
            const g_id = `task_group_${group.id}`;
            const is_visible = allNodesAreOpen(group.id);
            const active = (group.id === current);
            const gclass = is_visible ? 'sidebar__group-visible' + (active ? ' active' : '') : 'sidebar__group-hidden';

            if (group.is_leaf) {
                const href = `/${app}/?${entity}=${group.id}`;
                const item_class = `bi-journals level-${group.level}`;
                itemLink = (
                    <a id={g_id} key={group.id} href={href} data-id={group.id} data-parent={group.node_id} className={gclass} aria-current={active}>
                        <div>
                            <i className={item_class}></i>
                            <span className="group-item-title">{item.name}</span>
                        </div>
                        <span>{item.act_items_qty}</span>
                    </a>
                );
            } else {
                const folder_class = `bi-folder2${group.is_open ? '-open' : ''} level-${group.level}`;
                const chevron_class = `bi-chevron-${group.is_open ? 'down' : 'left'}`;
                itemLink = (
                    <button id={g_id} key={group.id} data-id={group.id} data-parent={group.node_id} className={gclass} onClick={handleClick}>
                        <div>
                            <i className={folder_class}></i>
                            <span className="group-item-title">{item.name}</span>
                        </div>
                        <i className={chevron_class}></i>
                    </button>
                );
            }

            return itemLink;
        });

        groups = <div id="groups-tree" className="sidebar__groups">{groupList}</div>;
    }

    return groups;
}
    
export default GroupTree;