import { apiUrl } from '../auth/Auth';
import type { MouseEvent } from 'react'
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
        const sgId = item.sub_group_id;
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

async function toggleSubGroup(event: MouseEvent<HTMLElement>) {
    let el = event.target as HTMLElement;
    if (el.tagName !== 'BUTTON' && el.parentElement) {
        el = el.parentElement;
    }
    if (el.dataset.id) {
        const sgId = +el.dataset.id;
        const strSgId = `id-sub-group-${sgId}`;
        const hidden = document.getElementById(strSgId);
        if (hidden) {
            hidden.classList.toggle('d-none');
        }
        if (hidden) {
            el.children[0].classList.remove('bi-chevron-down');
            el.children[0].classList.add('bi-chevron-right');
        } else {
            el.children[0].classList.remove('bi-chevron-right');
            el.children[0].classList.add('bi-chevron-down');
        }
        if (el.dataset.group_id) {
            const grpId = +el.dataset.group_id;
            const cred: RequestCredentials = 'include';
            const headers =  {'Content-type': 'application/json'};
            const options = { 
                method: 'GET', 
                headers: headers,
                credentials: cred,
            };
            const url = `api/toggle_sub_group/`;
            const params = `?format=json&group_id=${grpId}&sub_group_id=${sgId}`;
            fetch(apiUrl +  url + params, options);
        }
    }
}

function SubGroup({subGroup, config}: {subGroup: SubGroupInfo, config: PageConfigInfo}) {
    const itemsList = subGroup.items.map(x => <ListItem key={x.id} item={x} config={config} />);
    if (!subGroup.name)
        return <>{itemsList}</>;

    const sgClass = `sub-group__icon bi-chevron-${subGroup.is_open ? 'down': 'right'}`;
    const sgId = `id-sub-group-${subGroup.id}`;
    const itemsClass = !subGroup.items.length || !subGroup.is_open ? 'd-none' : '';
    return (
        <div>
            <button className="sub-group" onClick={toggleSubGroup} data-id={subGroup.id} data-group_id={config.cur_view_group_id} >
                <i className={sgClass}></i>
                <span className="sub-group__name">{subGroup.name}</span>
                <span className="sub-group__qty">{subGroup.items.length}</span>
            </button>
            <ul id={sgId} className={itemsClass}>
                {itemsList}
            </ul>
        </div>
    );
}

export default SubGroup;