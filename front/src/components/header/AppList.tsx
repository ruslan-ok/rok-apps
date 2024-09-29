import { useMatch, useResolvedPath } from "react-router-dom";
import type { Application } from './Header';
import './AppList.css';

function AppLink({ mobile, app_name, icon, to }: { mobile: boolean, app_name: string, icon: string, to: string}) {
    const resolved = useResolvedPath(to);
    const match = useMatch({ path: resolved.pathname, end: true });
    const link_class = match ? 'active' : '';
    const btn_name = ((mobile || match) ? app_name : '');
    const app_icon = 'bi-' + icon;
  
    return (
        <li className={link_class} title={app_name}>
            <a className={link_class} href={to} aria-current={match}>
                <i className={app_icon}></i>
                <span>{btn_name}</span>
            </a>
        </li>
    );
}

function AppList({mobile, items}: {mobile: boolean, items: Application[]}) {
    let apps = <div className='desktop'></div>;

    if (items.length) {
        const applications = items.map((app) => {
            return <AppLink key={app.name} mobile={mobile} app_name={app.name} icon={app.icon} to={app.href} />
        });

        const section_class = 'application ' + (mobile ? 'mobile' : 'desktop');

        apps = 
            <div className={section_class}>
                <ul className=''>
                    {applications}
                </ul>
            </div>;
    }

    return apps;
}

export default AppList;
