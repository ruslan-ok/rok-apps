import { useState, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import { auth as api } from '../auth/Auth';
import type { PageConfigInfo } from './TodoPage';
import type { SubGroupInfo } from './SubGroup';
import { fillSubGroups } from './SubGroup';
import SubGroup from './SubGroup';
import PageTitle from './PageTitle';
import { ItemInfo } from './ItemTypes';

function TodoListPage() {
    const config = useOutletContext() as PageConfigInfo;
    const [cur_view_group_id, setGroup] = useState<number|undefined>(config.cur_view_group_id);
    const [data, setData] = useState<Object[]>([]);
    const [childrenChanged, setChildrenChanged] = useState<boolean>(false);
    useEffect(() => {
        const getData = async () => {
            let params = {};
            if (config.view)
                params = Object.assign(params, {view: config.view});
            if (config.group_id)
                params = Object.assign(params, {group: config.group_id});
            const data: ItemInfo[] = await api.get('todo', params);
            setData(data);
            setGroup(config.cur_view_group_id);
        };
      
        getData();
    }, [config, childrenChanged]);

    function updateFromChild() {
        setChildrenChanged(!childrenChanged);
    }

    function compareSG(a: SubGroupInfo, b: SubGroupInfo): number {
        return a.id - b.id;
    }

    const items = cur_view_group_id === config.cur_view_group_id ? data.map(x => {return new ItemInfo(x);}) : [];
    const subGroups: SubGroupInfo[] = fillSubGroups(items, config);
    const validSG = subGroups.filter(x => x.items.length).sort(compareSG);
    let sgList;
    if (validSG.length) {
        sgList = validSG.map(x => { return <SubGroup key={x.id} subGroup={x} config={config} update={updateFromChild} /> });
    } else {
        sgList = <></>;
    }

    const list_class = 'list-content theme-' + (config.theme_id ? `${config.theme_id}`: '14');
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
