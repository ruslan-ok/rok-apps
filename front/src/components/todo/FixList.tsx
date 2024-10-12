import { useState, useEffect } from "react";
import { redirect } from "react-router-dom";
import { auth, apiUrl } from '../auth/Auth';
import type { PageConfigInfo } from './TodoPage';
import type { FixItemInfo } from './FixItem';
import FixItem from './FixItem';

async function loadData(config: PageConfigInfo): Promise<FixItemInfo[]> {
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
    const params = `?format=json&app=${config.app}` + (config.view ? `&view=${config.view}` : '');
    const res = await fetch(apiUrl +  'api/fixed/' + params, options);
    const resp_data = await res.json();
    return resp_data;
}

function FixList({config}: {config: PageConfigInfo}) {
    const [items, setData] = useState<FixItemInfo[]>([]);
    useEffect(() => {
        const getData = async () => {
          const data = await loadData(config);
          const items = data as FixItemInfo[];
          setData(items);
        };
      
        getData();
    }, []);

    let fixes = <></>;

    if (items.length) {
        const fixList = items.map((item) => {
            return <FixItem key={item.id} item={item} />
        });
    
        fixes = <>{fixList}<hr/></>;
    }

    return <>{fixes}</>;
}
    
export default FixList;