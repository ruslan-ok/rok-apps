import { useState, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import { api } from '../../API'
import { IPageConfig } from '../PageConfig';
import type { SubGroupInfo } from './SubGroup';
import { fillSubGroups } from './SubGroup';
import SubGroup from './SubGroup';
import PageTitle from './PageTitle';
import { ItemInfo } from './ItemTypes';

function TodoListPage() {
    const config = useOutletContext() as IPageConfig;
    const [state, setState] = useState<string>('load');
    const [subGroups, setData] = useState<SubGroupInfo[]>([]);
    let childrenChanged = false;
    useEffect(() => {
        const getData = async () => {
            setState('load');
            let params = {};
            if (config.view_group.view_id)
                params = Object.assign(params, {view: config.view_group.view_id});
            if (config.entity.id)
                params = Object.assign(params, {group: config.entity.id});
            const data: ItemInfo[] = await api.get('todo', params);
            const items = data.map(x => {return new ItemInfo(x);});
            const sgList: SubGroupInfo[] = fillSubGroups(items, config.view_group.id, config.view_group.use_sub_groups);
            const validSG = sgList.filter(x => x.items.length).sort(compareSG);
            setData(validSG);
            setState('done');
        };
      
        getData();
    }, [config.entity.id, config.view_group.id, config.view_group.view_id, childrenChanged, config.view_group.use_sub_groups]);

    function updateFromChild() {
        childrenChanged = !childrenChanged;
    }

    function compareSG(a: SubGroupInfo, b: SubGroupInfo): number {
        return a.id - b.id;
    }

    let sgList;
    if (state === 'done' && subGroups.length) {
        sgList = subGroups.map(x => { return <SubGroup key={x.id} subGroup={x} config={config} update={updateFromChild} /> });
    } else {
        sgList = <></>;
    }

    const list_class = 'list-content theme-' + (config.view_group.theme ? `${config.view_group.theme}`: '8');
    return (
        <main>
            <div className={list_class}>
                <PageTitle config={config} />
                {sgList}
            </div>
        </main>
    );
}

export default TodoListPage;
