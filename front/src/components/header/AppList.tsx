import type { Application } from './Header';
import './AppList.css';

function AppList({mobile, items}: {mobile: boolean, items: Application[]}) {
    let apps = <div className='desktop'></div>;

    if (items.length) {
      const applications = items.map((app) => {
        let a_class = '';
        if (app.active) {
          a_class = 'active';
        }
        let icon = 'bi-' + app.icon;
        let name = '';
        if (mobile || app.active)
          name = app.name;
        return (
            <li className={a_class} key={app.name} title={app.name}>
              <a className={a_class} href={app.href } aria-current={app.active}>
                <i className={icon}></i>
                <span>{name}</span>
              </a>
            </li>
        );
      });

      let section_class = 'application ';
      if (mobile) {
        section_class += 'mobile';
      } else {
        section_class += 'desktop';
      }
  
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
