export interface NavItem {
    id: number;
    name: string;
    qty: number;
    href: string;
};

function NavList({items, current, entity}: {items: NavItem[], current: string | number | undefined, entity: string}) {
    let navs = <></>;

    if (items.length) {
        const navList = items.map((item) => {
            const id = `task_group_${item.id}`;
            const active = (item.id === current);
            const iclass = 'sidebar__group-visible' + (active ? ' active' : '');
            const href = `${item.href}?${entity}=${item.id}`
            const qty = item.qty ? `${item.qty}` : '';
            return (
                <a id={id} data-id={item.id} key={item.name} href={href} aria-current={active} className={iclass}>
                    <div>
                        <i className="bi-journals"></i>
                        <span>{item.name}</span>
                    </div>
                    <span>{qty}</span>
                </a>
            );
        });
    
        navs = <div id="groups-tree" className="sidebar__groups">{navList}<hr></hr></div>;
    }

    return navs;
}
    
export default NavList;