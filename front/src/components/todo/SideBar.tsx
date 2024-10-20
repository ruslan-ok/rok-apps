import { IPageConfig } from '../PageConfig';
import FixList from './FixList';
import GroupTree from './GroupTree';
import DirTree from './DirTree';
import NavList from './NavList';
import AddNewGroup from './AddNewGroup';
import '../css/sidebar.min.css'

function SideBar({config}: {config: IPageConfig}) {
    const useGroups = config.view_group.app === 'todo';
    return (
        <aside className="bd-sidebar">
            <nav className="bd-links collapse sidebar" id="bd-docs-nav" aria-label="Groups navigation">
                <FixList config={config} />
                {useGroups && <>
                        <DirTree config={config} />
                        <GroupTree config={config} />
                        <AddNewGroup config={config} />
                    </>
                }
                <NavList config={config} />
            </nav>
        </aside>
    );
}
    
export default SideBar;