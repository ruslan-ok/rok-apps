import { Link } from 'react-router-dom';
import { IPageConfig, IPathItem, EntityType } from '../PageConfig';
import ThemeSelector from './ThemeSelector';


function AddItem({config}: {config: IPageConfig}) {
    return <div className="btn bi-plus dark-theme"></div>;
}

function PageTitle({config}: {config: IPageConfig}) {
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

    let grpupsPath = <></>;
    if (config.entity.path.constructor === Array<IPathItem>) {
        const reversedGroups = config.entity.path.slice().reverse();
        const first: IPathItem = config.entity.path[0];
        grpupsPath = reversedGroups.map(group => {
            const url = `group/${group.id}?ret=${config.entity.id}`;
            const link = <Link to={url} className={config.checkDark('content-title__href')}>{group.name}</Link>
            const sep = group.id === first.id ? <></> : <h3 className={config.checkDark('content-title__separator')}>/</h3>;
            return (<span key={group.id} className="d-flex">{link}{sep}</span>);
        });
    }
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
    return (
        <div className="content-title d-flex justify-content-between">
            <div className="title d-none d-md-flex">
                {config.icon && <i className={config.iconClass}></i>}
                {grpupsPath}
                {!config.entity.path.length &&
                    <h3 className={config.checkDark('content-title__text')}>
                        {config.entity.type === EntityType.Folder && <>
                            <span>{config.folderPath}</span>
                            <span id="id_folder_view" className="folder_view">{config.entity.name}</span>
                            <span id="id_folder_edit" className="folder_edit d-none">
                                <input type="text" name="file_name" size="15" maxlength="100" value="zzz"/>
                            </span>
                        </>}
                        {config.entity.type !== EntityType.Folder && config.title}
                        {config.entity.type === EntityType.Folder && <>
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
                {config.add_item && <AddItem config={config} />}

                {config.sorts.length &&
                    <div className="dropdown">
                        <button type="button" id="dropdownMenuButton1" 
                            data-bs-toggle="dropdown" aria-expanded="false" className={config.checkDark('btn bi-sort-alpha-down')}></button>
                        <ul className="dropdown-menu" aria-labelledby="dropdownMenuButton1">
                            {sortButtons}
                        </ul>
                    </div>
                }

                <ThemeSelector config={config} />
            </div>
        </div>
    );
}
    
export default PageTitle;