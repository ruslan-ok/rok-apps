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

function FixItem({item}: {item: FixItemInfo}) {
    const link_class = 'sidebar__fix-item' + (item.active ? ' active' : '');
    const fix_icon = 'bi-' + item.icon;
    const qty = (item.search_qty ? `${item.search_qty} / ` : '') + (item.qty ? `${item.qty}` : '');
    return (
        <a href={item.url} aria-current={item.active} className={link_class}>
            <div>
                <i className={fix_icon}></i>
                <span className="group-item-title">{item.title}</span>
            </div>
            <span>{qty}</span>
        </a>
    );
}
    
export default FixItem;