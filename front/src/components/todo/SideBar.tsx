import type { PageConfigInfo } from './TodoPage'
import FixList from './FixList';
import GroupTree from './GroupTree';
import DirTree from './DirTree';
import NavList from './NavList';
import AddNewGroup from './AddNewGroup';
import '../css/sidebar.min.css'

function SideBar({config}: {config: PageConfigInfo}) {
    return (
        <aside className="bd-sidebar">
            <nav className="bd-links collapse sidebar" id="bd-docs-nav" aria-label="Groups navigation">
                <FixList config={config} />
                {config.use_groups && <>
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