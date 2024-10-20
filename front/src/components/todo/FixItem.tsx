import { Link } from 'react-router-dom';
import { IPageConfig } from '../PageConfig';

export interface FixItemInfo {
    id: string;
    url: string;
    icon: string;
    title: string;
    qty: number | null;
    search_qty: number | null;
    active: boolean;
    determinator: string;
}

function FixItem({item, config}: {item: FixItemInfo, config: IPageConfig}) {
    const link_class = 'sidebar__fix-item' + (item.active && !config.entity.id ? ' active' : '');
    const fix_icon = 'bi-' + item.icon;
    const qty = (item.search_qty ? `${item.search_qty} / ` : '') + (item.qty ? `${item.qty}` : '');
    return (
        <Link to={item.url} className={link_class}>
            <div>
                <i className={fix_icon}></i>
                <span className="group-item-title">{item.title}</span>
            </div>
            <span>{qty}</span>
        </Link>
    );
}
    
export default FixItem;