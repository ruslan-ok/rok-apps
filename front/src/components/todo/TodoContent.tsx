import { useState, useEffect } from "react";
import { redirect } from "react-router-dom";
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

function TodoContent({config}: {config: PageConfigInfo}) {
    const [data, setData] = useState<Object[]>([]);
    useEffect(() => {
        const getData = async () => {
          const data = await loadData(config);
          setData(data);
        };
      
        getData();
    }, [config]);

    function compareSG(a: SubGroupInfo, b: SubGroupInfo): number {
        return a.id - b.id;
    }

    const items = data.map(x => {return new ItemInfo(x);});
    const subGroups: SubGroupInfo[] = fillSubGroups(items, config);
    const validSG = subGroups.filter(x => x.items.length).sort(compareSG);
    let sgList;
    if (validSG.length) {
        sgList = validSG.map(x => { return <SubGroup key={x.id} subGroup={x} config={config} /> });
    } else {
        sgList = <></>;
    }

    const list_class = 'list-content' + (config.theme_id ? ` theme-${config.theme_id}`: '');
    return (
        <main>
            <div className={list_class}>
                <PageTitle config={config} />
                {sgList}
            </div>
        </main>
    );
}

export default TodoContent;