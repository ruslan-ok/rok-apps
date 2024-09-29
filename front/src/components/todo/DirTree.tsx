export interface DirItem {
    id: string;
    node: string;
    name: string;
    level: number;
    qty: number;
};

function DirTree({items, current, listHref, view}: {items: DirItem[], current: number | string | undefined, listHref: boolean, view: string}) {
    let dirs = <></>;

    if (items.length) {
        const dirList = items.map((dir) => {
            let href = '';
            if (listHref) {
                if (view) {
                    href = `view=${view}&`;
                }
                href += `folder=${dir.node}`;
                if (dir.node) {
                    href += '/';
                }
            }
            href += `${dir.name}`;

            const active = (href === current);
            const iclass = 'item hidden' + (active ? ' active' : '');
            const dclass = `bi-dot icon invisible level-${dir.level}`;
            const dirQty = dir.qty ? `${dir.qty}` : '';

            return (
                <div key={dir.id} className={iclass} aria-current={active} data-parent={dir.node} data-name={dir.name}>
                    <div>
                        <i type="button" role="button" className={dclass}></i>
                        <i className="bi-folder2"></i>
                        <a href={href}>{dir.name}</a>
                    </div>
                    <span className="qty">{dirQty}</span>
                </div>
            );
        });

        dirs = <div id="dirs-tree" className="dirs">{dirList}</div>;
    }

    return dirs;
}
    
export default DirTree;