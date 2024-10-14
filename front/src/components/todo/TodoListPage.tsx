import { useState, useEffect } from "react";
import { redirect, useOutletContext } from "react-router-dom";
import { auth, apiUrl } from '../auth/Auth';
import type { PageConfigInfo } from './TodoPage';
import type { SubGroupInfo } from './SubGroup';
import { fillSubGroups } from './SubGroup';
import SubGroup from './SubGroup';
import PageTitle from './PageTitle';
import { ItemInfo } from './ItemTypes';

export async function loadData(config: PageConfigInfo): Promise<ItemInfo[]> {
    await auth.init();
    if (!auth.isAuthenticated) {
        throw redirect('/login');
    }
    const cred: RequestCredentials = 'include';
    const headers =  {'Content-type': 'application/json'};
    const options = { 
      method: 'GET', 
      headers: headers,
      credentials: cred,
    };
    const params = `?format=json` + (config.view ? `&view=${config.view}` : '') + (config.group_id ? `&group=${config.group_id}` : '');
    const res = await fetch(apiUrl +  'api/todo/' + params, options);
    const resp_data = await res.json();
    return resp_data;
}

function TodoListPage() {
    const config = useOutletContext() as PageConfigInfo;
    const [cur_view_group_id, setGroup] = useState<number|undefined>(config.cur_view_group_id);
    const [data, setData] = useState<Object[]>([]);
    useEffect(() => {
        const getData = async () => {
          const data = await loadData(config);
          setData(data);
          setGroup(config.cur_view_group_id);
        };
      
        getData();
    }, [config]);

    function compareSG(a: SubGroupInfo, b: SubGroupInfo): number {
        return a.id - b.id;
    }

    const items = cur_view_group_id === config.cur_view_group_id ? data.map(x => {return new ItemInfo(x);}) : [];
    const subGroups: SubGroupInfo[] = fillSubGroups(items, config);
    const validSG = subGroups.filter(x => x.items.length).sort(compareSG);
    let sgList;
    if (validSG.length) {
        sgList = validSG.map(x => { return <SubGroup key={x.id} subGroup={x} config={config} /> });
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
