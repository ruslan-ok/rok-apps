export interface FixItem {
    id: string;
    url: string;
    icon: string;
    title: string;
    qty: number | null;
    active: boolean;
    search_qty: number | null;
};

function FixList({items}: {items: FixItem[]}) {
    let fixes = <></>;

    if (items.length) {
        const fixList = items.map((item) => {
            const active = (item.active);
            const iclass = 'sidebar__fix-item' + (active ? ' active' : '');
            const icon = 'bi-' + item.icon;
            const qty = (item.search_qty ? `${item.search_qty} / ` : '') + (item.qty ? `${item.qty}` : '');
            return (
                <a key={item.id} href={item.url} aria-current={active} className={iclass}>
                    <div>
                        <i className={icon}></i>
                        <span className="group-item-title">{item.title}</span>
                    </div>
                    <span>{qty}</span>
                </a>
            );
        });
    
        fixes = <>{fixList}<hr></hr></>;
    }

    return fixes;
}
    
export default FixList;