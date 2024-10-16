import { useState, useEffect } from "react";
import { auth as api } from '../auth/Auth';
import type { PageConfigInfo } from './TodoPage';
import type { FixItemInfo } from './FixItem';
import FixItem from './FixItem';

function FixList({config}: {config: PageConfigInfo}) {
    const [items, setData] = useState<FixItemInfo[]>([]);
    useEffect(() => {
        const getData = async () => {
            let params = {app: config.app};
            if (config.view)
                params = Object.assign(params, {view: config.view});
            const items: FixItemInfo[] = await api.get('fixed', params);
            setData(items);
        };
      
        getData();
    }, [config]);

    let fixes = <></>;

    if (items.length) {
        const fixList = items.map((item) => {
            return <FixItem key={item.id} item={item} config={config} />
        });
    
        fixes = <>{fixList}<hr/></>;
    }

    return <>{fixes}</>;
}
    
export default FixList;