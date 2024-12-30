import { useState, useEffect } from "react";
import { ListGroup } from 'react-bootstrap';
import { api } from '../../API'
import { IPageConfig } from '../PageConfig';
import { IFixItemInfo } from './FixItem';
import FixItem from './FixItem';

function FixList({config}: {config: IPageConfig}) {
    const [items, setData] = useState<IFixItemInfo[]>([]);
    useEffect(() => {
        const getData = async () => {
            let params = {app: config.view_group.app};
            if (config.view_group.view_id)
                params = Object.assign(params, {view: config.view_group.view_id});
            else
                params = Object.assign(params, {group: config.view_group.id});
            const items: IFixItemInfo[] = await api.get('fixed', params);
            setData(items);
        };
      
        getData();
    }, [config]);

    let fixes = <></>;

    if (items.length) {
        const fixList = items.map((item) => {
            return <FixItem key={item.id} item={item} config={config} />
        });
    
        fixes = (
            <ListGroup className="mb-3">
                {fixList}
            </ListGroup>
        );
    }

    return <>{fixes}</>;
}
    
export default FixList;