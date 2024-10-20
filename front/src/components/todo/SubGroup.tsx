import { useState } from "react";
import type { MouseEvent } from 'react'
import { IPageConfig } from '../PageConfig';
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
    groupId: number;
    kind: SubGroupKind;
    is_open: boolean;
    items: Array<ItemInfo>;

    constructor(groupId: number, kind: SubGroupKind) {
        this.groupId = groupId;
        this.kind = kind;
        this.is_open = this.loadIsOpen();
        this.items = [];
    }

    loadIsOpen() {
        let value = localStorage.getItem('sg_' + this.id);
        if (value === 'true' || value === '1')
            return true;
        return false;
    }

    toggle() {
        this.is_open = !this.is_open;
        localStorage.setItem('sg_' + this.id, this.is_open ? 'true' : 'false');
    }

    get id() {
        return this.groupId * 100 + this.kind;
    }

    get name() {
        if (this.kind === SubGroupKind.EXPIRED)
            return 'Earlier';
        if (this.kind === SubGroupKind.TODAY)
            return 'Today';
        if (this.kind === SubGroupKind.TOMORROW)
            return 'Tomorrow';
        if (this.kind === SubGroupKind.THIS_WEEK)
            return 'On the week';
        if (this.kind === SubGroupKind.LATER)
            return 'Later';
        if (this.kind === SubGroupKind.COMPLETED)
            return 'Completed';
        return '';
    }

    addItem(item: ItemInfo) {
        this.items.push(item);
    }
}

export function fillSubGroups(data: ItemInfo[], group_id: number, use_sub_groups: boolean) {
    let subGroups: SubGroupInfo[] = [];
    for (const item of data) {
        const kind = use_sub_groups ? item.sub_group_id : 0;
        let sg = subGroups.find(x => x.groupId === group_id && +x.kind === +kind);
        if (!sg) {
            sg = new SubGroupInfo(group_id, kind);
            subGroups.push(sg);
        }
        sg.addItem(item);
    }
    return subGroups;
}

function _toggleSubGroup(event: MouseEvent<HTMLElement>, groupId: number, subGroupId: number, isOpen: boolean) {
    const elItems = document.getElementById(`items-for-sub-group-${subGroupId}`);
    let elButton = event.target as HTMLElement;
    if (elButton.tagName !== 'BUTTON' && elButton.parentElement) {
        elButton = elButton.parentElement;
    }
    if (!elItems || !elButton)
        throw new Error('Error on rendering SubGroup.');

    if (isOpen) {
        elItems.classList.remove('d-none');
        elButton.children[0].classList.remove('bi-chevron-right');
        elButton.children[0].classList.add('bi-chevron-down');
    } else {
        elItems.classList.add('d-none');
        elButton.children[0].classList.remove('bi-chevron-down');
        elButton.children[0].classList.add('bi-chevron-right');
    }
}

function SubGroup({subGroup, config, update}: {subGroup: SubGroupInfo, config: IPageConfig, update: Function}) {
    const [sg, setSG] = useState<SubGroupInfo>(subGroup);
    function toggleSubGroup(event: MouseEvent<HTMLElement>) {
        sg.toggle();
        setSG(sg);
        _toggleSubGroup(event, config.view_group.id, sg.id, sg.is_open);
    }
    const sgClass = `sub-group__icon bi-chevron-${sg.is_open ? 'down': 'right'}`;
    const sgId = `items-for-sub-group-${sg.id}`;
    const showSG = sg.name && config.view_group.use_sub_groups && sg.items.length;
    const itemsClass = showSG && !sg.is_open ? 'd-none' : '';
    const itemsVisible = !showSG || sg.is_open;
    const itemsList = sg.items.map(x => <ListItem key={x.id} item={x} visible={itemsVisible} config={config} update={update} />);
    return (
        <div>
            {showSG &&
                <button className="sub-group" onClick={toggleSubGroup} >
                    <i className={sgClass}></i>
                    <span className="sub-group__name">{sg.id} - {sg.name}</span>
                    <span className="sub-group__qty">{sg.items.length}</span>
                </button>
            }
            <ul id={sgId} className={itemsClass}>
                {itemsList}
            </ul>
        </div>
    );
}

export default SubGroup;