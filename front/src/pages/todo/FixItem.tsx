import { Link } from 'react-router-dom';
import { ListGroup } from 'react-bootstrap';
import { IPageConfig } from '../PageConfig';

export interface IFixItemInfo {
    id: string;
    url: string;
    icon: string;
    title: string;
    qty: number | null;
    search_qty: number | null;
    active: boolean;
    determinator: string;
}

function FixItem({item, config}: {item: IFixItemInfo, config: IPageConfig}) {
    // const link_class = 'd-flex justify-content-between text-decoration-none text-secondary-emphasis' + (item.active && !config.entity.id ? ' active' : '');
    // const link_class = 'text-decoration-none'; //'d-flex justify-content-between text-decoration-none text-secondary-emphasis' + (item.active && !config.entity.id ? ' active' : '');
    const fix_icon = 'me-2 bi-' + item.icon;
    const qty = (item.search_qty ? `${item.search_qty} / ` : '') + (item.qty ? `${item.qty}` : '');
    return (
        <ListGroup.Item action active={item.active} className="p-1" href={item.url}>
            <div>
                <i className={fix_icon}></i>
                <span className="group-item-title">{item.title}</span>
            </div>
            <span>{qty}</span>
        </ListGroup.Item>
    );
}
    
export default FixItem;