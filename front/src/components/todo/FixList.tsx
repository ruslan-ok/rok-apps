import { useState, useEffect } from "react";
import { api } from '../../API'
import { IPageConfig } from '../PageConfig';
import { FixItemInfo } from './FixItem';
import FixItem from './FixItem';

function FixList({config}: {config: IPageConfig}) {
    const [items, setData] = useState<FixItemInfo[]>([]);
    useEffect(() => {
        const getData = async () => {
            let params = {app: config.view_group.app};
            if (config.view_group.view_id)
                params = Object.assign(params, {view: config.view_group.view_id});
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