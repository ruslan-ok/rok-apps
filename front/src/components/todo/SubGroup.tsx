import { useState } from "react";
import type { MouseEvent } from 'react'
import { auth as api } from '../auth/Auth';
import type { PageConfigInfo } from './TodoPage';
import { ItemInfo } from './ItemTypes';
import ListItem from './ListItem';


export enum SubGroupKind {
    UNKNOWN = 0, // Не определено
    EXPIRED = 1, // Просрочено
    TODAY = 2, // Сегодня
    TOMORROW = 3, // Завтра
    THIS_WEEK = 4, // На этой неделе
    LATER = 5, // Позже
    COMPLETED = 6, // Завершено
}

export class SubGroupInfo {
    id: SubGroupKind;
    is_open: boolean;
    items: Array<ItemInfo>;

    constructor(id: SubGroupKind) {
        this.id = id;
        this.is_open = false;
        this.items = [];
    }

    get name() {
        if (this.id === SubGroupKind.EXPIRED)
            return 'Earlier';
        if (this.id === SubGroupKind.TODAY)
            return 'Today';
        if (this.id === SubGroupKind.TOMORROW)
            return 'Tomorrow';
        if (this.id === SubGroupKind.THIS_WEEK)
            return 'On the week';
        if (this.id === SubGroupKind.LATER)
            return 'Later';
        if (this.id === SubGroupKind.COMPLETED)
            return 'Completed';
        return '';
    }

    addItem(item: ItemInfo) {
        this.items.push(item);
    }
}

export function fillSubGroups(data: ItemInfo[], config: PageConfigInfo) {
    let subGroups: SubGroupInfo[] = [];
    for (const item of data) {
        const sgId = config.use_sub_groups ? item.sub_group_id : 0;
        let sg = subGroups.find(x => +x.id === +sgId);
        if (!sg) {
            sg = new SubGroupInfo(sgId);
            if (sg !== undefined && config.sub_groups) {
                const state = config.sub_groups.filter(x => x.id === sg.id);
                if (state.length === 1)
                    sg.is_open = state[0].is_open;
            }
            subGroups.push(sg);
        }
        sg.addItem(item);
    }
    return subGroups;
}

async function _toggleSubGroup(event: MouseEvent<HTMLElement>) {
    const {group_id, sub_group_id} = api.buttonData(event, ['group_id', 'sub_group_id']);
    const strSgId = `id-sub-group-${+sub_group_id}`;
    const hidden = document.getElementById(strSgId);
    if (hidden) {
        hidden.classList.toggle('d-none');
    }
    let el = event.target as HTMLElement;
    if (el.tagName !== 'BUTTON' && el.parentElement) {
        el = el.parentElement;
    }
    if (hidden && hidden.classList.contains('d-none')) {
        el.children[0].classList.remove('bi-chevron-down');
        el.children[0].classList.add('bi-chevron-right');
    } else {
        el.children[0].classList.remove('bi-chevron-right');
        el.children[0].classList.add('bi-chevron-down');
    }
    await api.post(`group/${+group_id}/toggle_sub_group`, {sub_group_id: +sub_group_id});
}

function SubGroup({subGroup, config, update}: {subGroup: SubGroupInfo, config: PageConfigInfo, update: Function}) {
    const [is_open, setIsOpen] = useState<boolean>(subGroup.is_open);
    async function toggleSubGroup(event: MouseEvent<HTMLElement>) {
        const new_is_open = !is_open;
        setIsOpen(new_is_open);
        await _toggleSubGroup(event);
    }
    const sgClass = `sub-group__icon bi-chevron-${subGroup.is_open ? 'down': 'right'}`;
    const sgId = `id-sub-group-${subGroup.id}`;
    const showSG = subGroup.name && config.use_sub_groups && subGroup.items.length;
    const itemsClass = showSG && !subGroup.is_open ? 'd-none' : '';
    const itemsVisible = !showSG || is_open;
    const itemsList = subGroup.items.map(x => <ListItem key={x.id} item={x} visible={itemsVisible} config={config} update={update} />);
    return (
        <div>
            {showSG &&
                <button className="sub-group" onClick={toggleSubGroup} data-group_id={config.cur_view_group_id} data-sub_group_id={subGroup.id} >
                    <i className={sgClass}></i>
                    <span className="sub-group__name">{subGroup.name}</span>
                    <span className="sub-group__qty">{subGroup.items.length}</span>
                </button>
            }
            <ul id={sgId} className={itemsClass}>
                {itemsList}
            </ul>
        </div>
    );
}

export default SubGroup;