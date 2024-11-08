import { IGroup } from '../ItemTypes';


function ItemGroup({group_id, groups}: {group_id: number, groups: IGroup[]}) {
    const groupList = groups.map(g => {return <option value={g.id}>{g.name}</option>});
    return (
        <div className="col-sm">
            <label htmlFor="id_grp">Group:</label>
            <select name="grp" className="form-control mb-3" id="id_grp">
                {groupList}
            </select>
        </div>
    );
}

export default ItemGroup;