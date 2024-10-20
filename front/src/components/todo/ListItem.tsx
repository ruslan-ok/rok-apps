import type { MouseEvent } from 'react'
import { useState, useEffect } from "react";
import { Link } from 'react-router-dom';
import { auth as api } from '../auth/Auth';
import { IPageConfig } from '../PageConfig';
import { ItemInfo, ExtraInfo } from './ItemTypes';
import '../css/category.min.css'


function Completed({item, config, update}: {item: ItemInfo, config: IPageConfig, update: Function}) {
    const [itemCompleted, setCompleted] = useState<boolean>(item.completed);

    function changeCompleted(newValue: boolean) {
        setCompleted(newValue);
        update();
    }

    async function toggleCompleted(event: MouseEvent<HTMLElement>) {
        const {todo_id, completed} = api.buttonData(event, ['todo_id', 'completed']);
        const newCompleted = completed !== 'true';
        changeCompleted(newCompleted);
        await api.put(`todo/${todo_id}`, {completed: newCompleted});
    }
    
    if (!config.use_selector)
        return <></>;
    const completedClass = itemCompleted ? 'bi-check-circle-fill' : 'bi-circle';
    return (
        <button onClick={toggleCompleted} className="left-icon" data-todo_id={item.id} data-completed={itemCompleted} >
            <i className={completedClass}></i>
        </button>
    );
}

function Roles({extra, config}: {extra: ExtraInfo, config: IPageConfig}) {
    if (!extra.roles || !extra.roles.length || config.view_group.role !== 'search')
        return <></>;
    const content = extra.roles.map(role => {
        const href = role.href + (role.hide_params ? '' : role.params);
        const icon = `bi-${role.icon}`;
        return <a key={role.href} href={href} className="left-icon"><i className={icon}></i></a>
    });
    return content;
}

function Name({item, extra, config}: {item: ItemInfo, extra: ExtraInfo, config: IPageConfig}) {
    let roles = <></>;
    if (config.view_group.role !== 'search' && extra.roles && extra.roles.length > 1) {
        const roleList = extra.roles.map(role => {
            if (role.name_mod === config.view_group.app)
                return <></>;
            const role_icon = `bi-${role.icon}`;
            return (
                <object key={role.href}>
                    <a href={role.href} className="role-icon">
                        <i className={role_icon}></i>
                    </a>
                </object>
            );
        });
        roles = (
            <span className="roles">
                {roleList}
            </span>
        );
    }

    const nameClass = `name${item.completed && config.use_selector ? ' completed' : ''}`;
    const name = `${config.event_in_name ? item.event + (item.name ? ' - ' : ''): ''}${item.name}`;
    return (
        <span className={nameClass}>
            {name}
            {roles}
        </span>
    );
}

function Group({item, extra, config}: {item: ItemInfo, extra: ExtraInfo, config: IPageConfig}) {
    if ((config.view_group.determinator !== 'role' && config.view_group.determinator !== 'view') || !extra.group_name)
        return <></>;
    return (
        <div className="inline">
            <div className="label"><span>{extra.group_name}</span></div>
            <i className="bi-dot"></i>
        </div>
    );
}

function Attributes({item, extra, config}: {item: ItemInfo, extra: ExtraInfo, config: IPageConfig}) {
    let attrs = [];
    const today = new Date();
    if (item.remind && !item.completed) {
        const remind = new Date(item.remind);
        if (remind > today) {
            attrs.push({icon: 'bi-bell'});
        }
    }
    if (item.in_my_day && (config.view_group.determinator !== 'view' || config.view_group.view_id !== 'myday')) {
        attrs.push({icon: 'bi-sun'});
        attrs.push({text: 'My day'});
        attrs.push({icon: 'bi-dot'});
    }
    if (extra.step_total > 0) {
        attrs.push({text: `${extra.step_completed} out of ${extra.step_total}`})
        attrs.push({icon: 'bi-dot'});
    }
    if (item.termin && !item.completed) {
        const atclass = item.is_expired ? 'expired' : 'actual';
        attrs.push({icon: 'bi-check2-square ' + atclass});
        attrs.push({atclass: atclass, text: item.termin_info});
        if (item.repeat)
            attrs.push({icon: 'bi-arrow-repeat ' + atclass});
        attrs.push({icon: 'bi-dot'});
    }
    if (item.completed) {
        attrs.push({text: `Completion ${item.Completion}`})
    }


    let attrList;
    if (!attrs.length)
        attrList = <></>;
    else {
        attrList = attrs.map((attr, index) => {
            if (attr.icon) {
                return <i key={index} className={attr.icon}></i>;
            }
            if (attr.text || attr.atclass) {
                const atclass = attr.atclass ? `label ${attr.atclass}` : 'label';
                return <div key={index} className={atclass}><span>{attr.text}</span></div>;
            }
            return <></>;
        });
    }
    return (
        <div className="inline">
            {attrList}
        </div>
    );
}

function Icons({item, extra}: {item: ItemInfo, extra: ExtraInfo}) {
    const has_files = extra.has_files ? <><i className="bi-paperclip"></i><i className="bi-dot"></i></> : <></>;
    const has_links = extra.has_links ? <><i className="bi-cursor"></i><i className="bi-dot"></i></> : <></>;
    const info = !item.info ? '' : item.info.replace(String.fromCharCode(13), '').replace(String.fromCharCode(10), '');
    const info_cut = info.substring(0, 79) + ((info.length > 80) ? '...' : '');
    const task_descr = info_cut ? (<>
        <i className="bi-sticky"></i>
        <div className="label">
            <span>{info_cut}</span>
        </div>
        <i className="bi-dot"></i>
    </>) : <></>;
    return (
        <div className="inline">
            {has_files}
            {has_links}
            {task_descr}
        </div>        
    );
}

const CATEGORY_DESIGN = [
    'green',
    'blue',
    'red',
    'purple',
    'yellow',
    'orange'
]

function getCategoryDesign(category: string): string {
    const sum = category.split('').reduce((x, y) => x + y.charCodeAt(0), 0);
    return CATEGORY_DESIGN[sum % 6];
}

function Categories({item}: {item: ItemInfo}) {
    const categories = item.categories?.length ? item.categories?.split(',') : [];
    const categs = categories.map((category, index) => {
        const categClass = `inline category-design-${getCategoryDesign(category)}`;
        return (
            <div key={index} className={categClass}>
                <i className="bi-circle"></i>
                <div className="label"><span>{category}</span></div>
            </div>
        );
    });
    return <>{categs}</>;
}

function Descr({item, extra, config}: {item: ItemInfo, extra: ExtraInfo, config: IPageConfig}) {
    return (
        <div className="descr">
            <Group item={item} extra={extra} config={config} />
            <Attributes item={item} extra={extra} config={config} />
            <Icons item={item} extra={extra} />
            <Categories item={item} />
        </div>
    );
}

function Tile({item, extra, config}: {item: ItemInfo, extra: ExtraInfo, config: IPageConfig}) {
    let href = `${item.id}`;
    return (
        <Link to={href} className="container info">
            <div className="info">
                <Name item={item} extra={extra} config={config} />
                <Descr item={item} extra={extra} config={config} />
            </div>
        </Link>
    );
}

function Important({item, config}: {item: ItemInfo, config: IPageConfig}) {

    const [itemImportant, setImportant] = useState<boolean>(item.important);

    async function toggleImportant(event: MouseEvent<HTMLElement>) {
        const {todo_id, important} = api.buttonData(event, ['todo_id', 'important']);
        const newImportant = important !== 'true';
        setImportant(newImportant);
        await api.put(`todo/${todo_id}`, {important: newImportant});
    }
        
    if (!config.use_star)
        return <></>;
    const importantClass = 'bi-star' + (itemImportant ? '-fill' : '');
    return (
        <button onClick={toggleImportant} className="right-icon" data-todo_id={item.id} data-important={itemImportant} >
            <i className={importantClass}></i>
        </button>
    );
}

function ListItem({item, visible, config, update}: {item: ItemInfo, visible: boolean, config: IPageConfig, update: Function}) {
    const emptyExtra: ExtraInfo = {
        initialized: false,
        roles: [],
        params: '',
        group_name: null,
        attributes: [],
        remind_active: false,
        step_completed: 0,
        step_total: 0,
        has_files: false,
        has_links: false,
        task_descr: '',
    };
    const [extra, setData] = useState<ExtraInfo>(emptyExtra);
    useEffect(() => {
        const getData = async () => {
            const data = await api.get(`todo/${item.id}/extra`, {app: config.view_group.app, role: config.view_group.role});
            const extra: ExtraInfo = Object.assign(data, {'initialized': true});
            setData(extra);
        };
        if (visible && !extra.initialized)
            getData();
    }, [item, visible, config, extra.initialized]);

    const item_class = `list-item${!config.use_selector && config.view_group.role !== 'search' ? ' px-3' : ''}`;
    return (
        <li className={item_class}>
            <Completed item={item} config={config} update={update} />
            <Roles extra={extra} config={config} />
            <Tile item={item} extra={extra} config={config} />
            <Important item={item} config={config} />
        </li>
    );
}

export default ListItem;