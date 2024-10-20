import { useState, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import { auth as api } from '../auth/Auth';
import { IPageConfig } from '../PageConfig';
import type { SubGroupInfo } from './SubGroup';
import { fillSubGroups } from './SubGroup';
import SubGroup from './SubGroup';
import PageTitle from './PageTitle';
import { ItemInfo } from './ItemTypes';

function TodoListPage() {
    const config = useOutletContext() as IPageConfig;
    const [data, setData] = useState<Object[]>([]);
    let childrenChanged = false;
    useEffect(() => {
        const getData = async () => {
            let params = {};
            if (config.view_group.view_id)
                params = Object.assign(params, {view: config.view_group.view_id});
            if (config.entity.id)
                params = Object.assign(params, {group: config.entity.id});
            const data: ItemInfo[] = await api.get('todo', params);
            setData(data);
            console.log('Data loaded for ' + JSON.stringify(params));
        };
      
        getData();
    }, [config.entity.id, config.view_group.id, config.view_group.view_id, childrenChanged]);

    function updateFromChild() {
        childrenChanged = !childrenChanged;
    }

    function compareSG(a: SubGroupInfo, b: SubGroupInfo): number {
        return a.id - b.id;
    }

    const items = data.map(x => {return new ItemInfo(x);});
    const subGroups: SubGroupInfo[] = fillSubGroups(items, config);
    console.log('Sub groups loaded for ' + config.view_group.id);
    const validSG = subGroups.filter(x => x.items.length).sort(compareSG);
    let sgList;
    if (validSG.length) {
        sgList = validSG.map(x => { return <SubGroup key={x.id} subGroup={x} config={config} update={updateFromChild} /> });
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
