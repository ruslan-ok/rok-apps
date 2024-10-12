import { useState, useEffect } from "react";
import { apiUrl } from '../auth/Auth';
import type { PageConfigInfo } from './TodoPage';
import { ItemInfo, ExtraInfo } from './ItemTypes';
import '../css/category.min.css'


function toggleCompleted(e) {
    console.log(e); // "toggleCompleted({{ item.id|escape }})"
}

function toggleImportant(e) {
    console.log(e); // "toggleImportant({{ item.id|escape }})"
}

function Completed({item, config}: {item: ItemInfo, config: PageConfigInfo}) {
    if (!config.use_selector)
        return <></>;
    const completedClass = item.completed ? 'bi-check-circle-fill' : 'bi-circle';
    return (
        <button onClick={toggleCompleted} className="left-icon">
            <i className={completedClass}></i>
        </button>
    );
}

function Roles({extra, config}: {extra: ExtraInfo, config: PageConfigInfo}) {
    if (!extra.roles || !extra.roles.length || config.role !== 'search')
        return <></>;
    const content = extra.roles.map(role => {
        const href = role.href + (role.hide_params ? '' : role.params);
        const icon = `bi-${role.icon}`;
        return <a key={role.href} href={href} className="left-icon"><i className={icon}></i></a>
    });
    return content;
}

function Name({item, extra, config}: {item: ItemInfo, extra: ExtraInfo, config: PageConfigInfo}) {
    let roles = <></>;
    if (config.role !== 'search' && extra.roles && extra.roles.length > 1) {
        const roleList = extra.roles.map(role => {
            if (role.name_mod === config.app)
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

function Group({item, extra, config}: {item: ItemInfo, extra: ExtraInfo, config: PageConfigInfo}) {
    if ((config.determinator !== 'role' && config.determinator !== 'view') || !extra.group_name)
        return <></>;
    return (
        <div className="inline">
            <div className="label"><span>{extra.group_name}</span></div>
            <i className="bi-dot"></i>
        </div>
    );
}

function Attributes({item, extra, config}: {item: ItemInfo, extra: ExtraInfo, config: PageConfigInfo}) {
    let attrs = [];
    const today = new Date();
    if (item.remind && !item.completed) {
        const remind = new Date(item.remind);
        if (remind > today) {
            attrs.push({icon: 'bi-bell'});
        }
    }
    if (item.in_my_day) {
        attrs.push({icon: 'bi-sun'});
        attrs.push({text: 'My day'});
    }
    if (item.termin && !item.completed) {
        const atclass = item.is_expired ? 'expired' : 'actual';
        attrs.push({icon: 'bi-check2-square ' + atclass});
        attrs.push({atclass: atclass, text: item.termin_info});
        if (item.repeat)
            attrs.push({icon: 'bi-arrow-repeat ' + atclass});
    }
    if (extra.step_total > 0) {
        attrs.push({text: `${extra.step_completed} out of ${extra.step_total}`})
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

function Icons({item, config}: {item: ItemInfo, config: PageConfigInfo}) {
    return <></>;
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

function Categories({item, config}: {item: ItemInfo, config: PageConfigInfo}) {
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

function Descr({item, extra, config}: {item: ItemInfo, extra: ExtraInfo, config: PageConfigInfo}) {
    return (
        <div className="descr">
            <Group item={item} extra={extra} config={config} />
            <Attributes item={item} extra={extra} config={config} />
            <Icons item={item} config={config} />
            <Categories item={item} config={config} />
        </div>
    );
}

function Tile({item, extra, config}: {item: ItemInfo, extra: ExtraInfo, config: PageConfigInfo}) {
    const href = `${extra.absolute_url}${extra.params}`;
    return (
        <a href={href} className="container info">
            <div className="info">
                <Name item={item} extra={extra} config={config} />
                <Descr item={item} extra={extra} config={config} />
            </div>
        </a>
    );
}

function Important({item, config}: {item: ItemInfo, config: PageConfigInfo}) {
    if (!config.use_important)
        return <></>;
    const importantClass = 'bi-star' + (item.important ? 'fill' : '');
    return (
        <button onClick={toggleImportant} className="right-icon">
            <i className={importantClass}></i>
        </button>
    );
}

async function loadData(item: ItemInfo, config: PageConfigInfo): Promise<ExtraInfo> {
    const cred: RequestCredentials = 'include';
    const headers =  {'Content-type': 'application/json'};
    const options = { 
      method: 'GET', 
      headers: headers,
      credentials: cred,
    };
    const params = `?format=json&role=${config.role}&app=${config.app}`;
    const res = await fetch(apiUrl + `api/todo_extra/${item.id}` + params, options);
    const resp_data = await res.json();
    return resp_data;
}

function ListItem({item, config}: {item: ItemInfo, config: PageConfigInfo}) {
    const emptyExtra = {
        roles: [],
        absolute_url: '',
        params: '',
        group_name: null,
        attributes: [],
        remind_active: false,
        step_completed: 0,
        step_total: 0,
    }
    const [extra, setData] = useState<ExtraInfo>(emptyExtra);
    useEffect(() => {
        const getData = async () => {
          const data = await loadData(item, config);
          const extra = data as ExtraInfo;
          setData(extra);
        };
      
        getData();
    }, [item, config]);

    const item_class = `list-item${!config.use_selector && config.role !== 'search' ? ' px-3' : ''}`;
    return (
        <li className={item_class}>
            <Completed item={item} config={config} />
            <Roles extra={extra} config={config} />
            <Tile item={item} extra={extra} config={config} />
            <Important item={item} config={config} />
        </li>
    );
}

export default ListItem;