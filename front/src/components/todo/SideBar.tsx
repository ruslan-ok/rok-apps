import type { FixItem } from './FixList';
import type { GroupItem } from './GroupTree';
import type { DirItem } from './DirTree';
import type { NavItem } from './NavList';
import FixList from './FixList';
import GroupTree from './GroupTree';
import DirTree from './DirTree';
import NavList from './NavList';
import AddNewGroup from './AddNewGroup';
import '../css/sidebar.min.css'

export interface SideBarData {
    fixes: FixItem[];
    use_groups: boolean;
    groups: GroupItem[];
    dirs: DirItem[];
    navs: NavItem[];
    list_href: boolean;
    cur_view: string;
    app: string;
    role: string;
    entity: string;
    current: number | string | undefined;
    create_group_hint: string;
};
  
function SideBar({data}: {data: SideBarData}) {

    let content = <></>;
    if (data) {
        content = <>
            <FixList items={data.fixes} />
            {data.use_groups && <>
                    <DirTree items={data.dirs} current={data.current} listHref={data.list_href} view={data.cur_view}/>
                    <GroupTree items={data.groups} current={data.current} app={data.app} entity={data.entity} />
                    <AddNewGroup app={data.app} role={data.role} entity={data.entity} hint={data.create_group_hint} />
                </>
            }
            <NavList items={data.navs} current={data.current} entity={data.entity} />
        </>;
    }
    return (
        <aside className="bd-sidebar">
            <nav className="bd-links collapse sidebar" id="bd-docs-nav" aria-label="Groups navigation">
                {content}
            </nav>
        </aside>
    );
}
    
export default SideBar;