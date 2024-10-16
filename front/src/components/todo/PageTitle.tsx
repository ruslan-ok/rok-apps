import type { MouseEvent } from 'react'
import { Link } from 'react-router-dom';
import { auth as api } from '../auth/Auth';
import type { PageConfigInfo } from './TodoPage';


function AddItem() {
    return <div className="btn bi-plus dark-theme"></div>;
}

function PageTitle({config}: {config: PageConfigInfo}) {
    function editFolder() {
        console.log('editFolder');
    }
    function delFolderConfirm() {
        console.log('delFolderConfirm');
    }
    function saveFolder() {
        console.log('saveFolder');
    }
    function delRole() {
        console.log('delRole');
    }
    function addRole() {
        console.log('addRole');
    }
    function setSort() {
        console.log('setSort');
    }

    async function setTheme(event: MouseEvent<HTMLElement>) {
        const {group_id, theme_id} = api.buttonData(event, ['group_id', 'theme_id']);
        await api.post(`group/${group_id}/theme`, {theme: theme_id});
    }

    async function toggleSubGroups(event: MouseEvent<HTMLElement>) {
        const {group_id, value} = api.buttonData(event, ['group_id', 'value']);
        const newValue = value !== 'true';
        await api.post(`group/${group_id}/use_groups`, {value: newValue});
    }
    
    const dark_theme = config.dark_theme ? ' dark-theme' : '';
    let iconClass = '';
    if (config.icon) {
        iconClass = `bi-${config.icon} content-title__icon${dark_theme}`;
    }

    const reversedGroups = config.group_path.slice().reverse();
    const grpupsPath = reversedGroups.map(group => {
        const url = `group/${group.id}?ret=${config.group_return}`;
        const hrefClass = `content-title__href${dark_theme}`;
        const sepClass = `content-title__separator${dark_theme}`;
        const link = <Link to={url} className={hrefClass}>{group.name}</Link>
        const sep = group.id === config.group_path[0].id ? <></> : <h3 className={sepClass}>/</h3>;
        return (<span key={group.id} className="d-flex">{link}{sep}</span>);
    });
    const relatedRoles = config.related_roles.map(role => {
        const roleId = `relRoleLink_${role.name}`;
        const title = `Related role is '${role.name}'`;
        const icon = `bi-${role.icon}`;
        return (<>
            <div key={role.name} className="dropdown">
                <a className="btn dropdown-toggle" href={role.href} role="button" id={roleId} 
                    data-bs-toggle="dropdown" aria-expanded="false">
                    <i className={icon} title={title}></i>
                </a>
                <ul className="dropdown-menu" aria-labelledby={roleId}>
                    <li><a className="dropdown-item" href={role.href}>Go to linked role</a></li>
                    <li><button type="button" className="dropdown-item" onClick={delRole}>Remove relation</button></li>
                </ul>
            </div>
        </>);
    });
    const possibleRelated = config.possible_related.map(role => {
        const icon = `btn possible-related bi-${role.icon}`;
        const roleId = `addRole_${role.name}`;
        const title = `Possible related role is '${role.name}'`;
        return <button key={role.name} className={icon} type="button" id={roleId} onClick={addRole} title={title}></button>;
    });
    const sortButtons = config.sorts.map(sort => {
        return <button key={sort.id} type="button" className="btn dropdown-item" onClick={setSort}>{sort.name}</button>;
    });
    const themeClass = `btn bi-gear${dark_theme}`;
    const themeButtons = config.themes.map(theme => {
        const btnClass = `btn theme ${theme.style}`;
        return <button key={theme.id} type="button" className={btnClass} onClick={setTheme} data-group_id={config.cur_view_group_id} data-theme_id={theme.id} ></button>;
    });
    const hdrClass = `content-title__text${dark_theme}`;
    const sortClass = `btn bi-sort-alpha-down${dark_theme}`;
    return (
        <div className="content-title d-flex justify-content-between">
            <div className="title d-none d-md-flex">
                {config.icon && <i className={iconClass}></i>}
                {grpupsPath}
                {!config.group_path.length &&
                    <h3 className={hdrClass}>
                        {config.folder && <>
                            <span>{config.path}</span>
                            <span id="id_folder_view" className="folder_view">{config.folder}</span>
                            <span id="id_folder_edit" className="folder_edit d-none">
                                <input type="text" name="file_name" size="15" maxlength="100" value="zzz"/>
                            </span>
                        </>}
                        {!config.folder && config.title}
                        {config.folder && <>
                            <button id="id_folder_edit_btn" className="bi-pen btn folder-mod-btn" onClick={editFolder}></button>
                            <button id="id_folder_del_btn" className="bi-trash btn folder-mod-btn" onClick={delFolderConfirm}></button>
                            <button id="id_folder_save_btn" className="bi-save btn folder-mod-btn d-none" onClick={saveFolder}></button>
                            <span id="id_edit_folder_error" className="d-none errornote">Error Description</span>
                        </>}
                    </h3>
                }
            </div>
            <div className="title d-md-none"></div>
            <div className="actions d-flex mx-2">
                <div className="related d-flex">
                    {relatedRoles}
                    {possibleRelated}
                </div>

                {!config.hide_add_item_input && <AddItem />}

                {config.sorts.length &&
                    <div className="dropdown">
                        <button type="button" id="dropdownMenuButton1" 
                            data-bs-toggle="dropdown" aria-expanded="false" className={sortClass}></button>
                        <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">
                            {sortButtons}
                        </ul>
                    </div>
                }

                {config.themes.length &&
                    <div className="dropdown mx-3">
                        <button className={themeClass} type="button" id="dropdownMenuButton1" data-bs-toggle="dropdown" 
                            data-bs-auto-close="false" aria-expanded="false"></button>
                        <ul className="dropdown-menu wide" aria-labelledby="dropdownMenuButton1">
                            <p>Theme</p>
                            {themeButtons}
                            {config.use_sub_groups &&
                                <div className="form-check form-switch my-1 mx-1">
                                    <input type="checkbox" name="use_sub_groups" id="id_use_sub_groups"
                                        className="form-check-input" onClick={toggleSubGroups} defaultChecked={config.use_sub_groups} />
                                    <label htmlFor="id_use_sub_groups" className="form-check-label">Use groups</label>
                                </div>
                            }
                        </ul>
                    </div>
                }


            </div>
        </div>
    );
}
    
export default PageTitle;