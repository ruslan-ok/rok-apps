import type { MouseEvent } from 'react'
import { api } from '../../API'
import { IPageConfig } from '../PageConfig';


// Wrong API: must use POST view_group
async function toggleSubGroups(event: MouseEvent<HTMLElement>) {
    const {group_id, value} = api.buttonData(event, ['group_id', 'value']);
    const newValue = value !== 'true';
    await api.post(`group/${group_id}/use_groups`, {value: newValue});
}

function ThemeSelector({config, setTheme}: {config: IPageConfig, setTheme: Function}) {
    async function selectTheme(event: MouseEvent<HTMLElement>) {
        const {group_id, group_name, theme_id} = api.buttonData(event, ['group_id', 'group_name', 'theme_id']);
        await api.put(`group/${group_id}/`, {name: group_name, theme: +theme_id});
        setTheme(+theme_id);
    }
    
    const themeButtons = config.themes.map(theme => {
        const btnClass = `btn btn-light theme ${theme.style}`;
        return <button key={theme.id} type="button" className={btnClass} onClick={selectTheme} data-group_id={config.view_group.id} data-group_name={config.view_group.name} data-theme_id={theme.id} ></button>;
    });

    return (<>
                {config.themes.length &&
                    <div className="dropdown">
                        <button className={config.checkDark('btn bi-gear')} type="button" id="themeDropdown" data-bs-toggle="dropdown" 
                            data-bs-auto-close="false" aria-expanded="false"></button>
                        <ul className="dropdown-menu wide" aria-labelledby="themeDropdown">
                            <h5>Theme</h5>
                            {themeButtons}
                            {config.view_group.use_sub_groups &&
                                <div className="form-check form-switch my-3 mx-1">
                                    <input type="checkbox" name="use_sub_groups" id="id_use_sub_groups"
                                        className="form-check-input" onClick={toggleSubGroups} defaultChecked={config.view_group.use_sub_groups} />
                                    <label htmlFor="id_use_sub_groups" className="form-check-label">Use groups</label>
                                </div>
                            }
                        </ul>
                    </div>
                }
    </>);
}

export default ThemeSelector;