import { useState, useEffect } from "react";
import { useOutletContext } from "react-router-dom";
import { api } from '../../API'
import { IPageConfig } from '../PageConfig';
import type { ISubGroup } from './SubGroup';
import { fillSubGroups } from './SubGroup';
import SubGroup from './SubGroup';
import PageTitle from './PageTitle';
import { IItemInfo } from './ItemTypes';


interface IPageData {
    state: string;
    subGroups: ISubGroup[] | null;
    themeId: number;
}

function TodoListPage() {
    const config = useOutletContext() as IPageConfig;
    const initialData = {
        state: 'load',
        subGroups: null,
        themeId: config.view_group.theme,
    };
    const [data, setState] = useState<IPageData>(initialData);

    let childrenChanged = false;
    useEffect(() => {
        const getData = async () => {
            let params = {};
            if (config.view_group.view_id)
                params = Object.assign(params, {view: config.view_group.view_id});
            if (config.entity.id)
                params = Object.assign(params, {group: config.entity.id});
            const itemData: IItemInfo[] = await api.get('todo', params);
            const items = itemData.map(x => {return new IItemInfo(x);});
            const sgList: ISubGroup[] = fillSubGroups(items, config.view_group.id, config.view_group.use_sub_groups);
            const validSG = sgList.filter(x => x.items.length).sort(compareSG);
            setState({
                state: 'done',
                subGroups: validSG,
                themeId: data.themeId,
            });
        };
      
        getData();
    }, [
        config.entity.id,
        config.view_group.id,
        config.view_group.view_id,
        childrenChanged, 
        config.view_group.use_sub_groups,
        data.themeId,
    ]);

    function setTheme(themeId: number) {
        setState({
            state: data.state,
            subGroups: data.subGroups,
            themeId: themeId,
        });
    }

    function updateFromChild() {
        childrenChanged = !childrenChanged;
    }

    function compareSG(a: ISubGroup, b: ISubGroup): number {
        return a.id - b.id;
    }

    let sgList;
    if (data.state === 'done' && data.subGroups?.length) {
        sgList = data.subGroups.map(x => { return <SubGroup key={x.id} subGroup={x} config={config} update={updateFromChild} /> });
    } else {
        sgList = <></>;
    }

    const list_class = 'list-content theme-' + (data.themeId ? `${data.themeId}`: '8');
    return (
        <main className="w-100">
            <div className={list_class}>
                <PageTitle config={config} setTheme={setTheme} />
                {sgList}
            </div>
        </main>
    );
}

export default TodoListPage;
