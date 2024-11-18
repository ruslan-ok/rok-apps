import type { MouseEvent } from 'react'
import { api } from '../../API'
import { IPageConfig } from '../PageConfig';


async function setTheme(event: MouseEvent<HTMLElement>) {
    const {group_id, theme_id} = api.buttonData(event, ['group_id', 'theme_id']);
    await api.post(`group/${group_id}/theme`, {theme: theme_id});
}

// Wrong API: must use POST view_group
async function toggleSubGroups(event: MouseEvent<HTMLElement>) {
    const {group_id, value} = api.buttonData(event, ['group_id', 'value']);
    const newValue = value !== 'true';
    await api.post(`group/${group_id}/use_groups`, {value: newValue});
}

function ThemeSelector({config}: {config: IPageConfig}) {
    const themeButtons = config.themes.map(theme => {
        const btnClass = `btn btn-light theme ${theme.style}`;
        return <button key={theme.id} type="button" className={btnClass} onClick={setTheme} data-group_id={config.view_group.id} data-theme_id={theme.id} ></button>;
    });
    return (<>
                {config.themes.length &&
                    <div className="dropdown mx-3">
                        <button className={config.checkDark('btn bi-gear fs-5')} type="button" id="dropdownMenuButton1" data-bs-toggle="dropdown" 
                            data-bs-auto-close="false" aria-expanded="false"></button>
                        <ul className="dropdown-menu wide" aria-labelledby="dropdownMenuButton1">
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