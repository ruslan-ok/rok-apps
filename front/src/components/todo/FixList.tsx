export interface FixItem {
    id: string;
    url: string;
    icon: string;
    title: string;
    qty: number | null;
    active: boolean;
    search_qty: number | null;
};

function FixLink({to, icon, title, qty, active}: {to: string, icon: string, title: string, qty: string, active: boolean}) {
    const link_class = 'sidebar__fix-item' + (active ? ' active' : '');
    const fix_icon = 'bi-' + icon;
  
    return (
        <a href={to} aria-current={active} className={link_class}>
            <div>
                <i className={fix_icon}></i>
                <span className="group-item-title">{title}</span>
            </div>
            <span>{qty}</span>
        </a>
    );
}

function FixList({items}: {items: FixItem[]}) {
    let fixes = <></>;

    if (items.length) {
        const fixList = items.map((item) => {
            const qty = (item.search_qty ? `${item.search_qty} / ` : '') + (item.qty ? `${item.qty}` : '');
            return <FixLink key={item.id} to={item.url} icon={item.icon} title={item.title} qty={qty} active={item.active} />
        });
    
        fixes = <>{fixList}<hr></hr></>;
    }

    return fixes;
}
    
export default FixList;