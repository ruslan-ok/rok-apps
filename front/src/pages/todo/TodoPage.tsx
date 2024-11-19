import { useEffect, useState } from "react";
import { redirect, useLoaderData, Outlet } from "react-router-dom";
import { api } from '../../API'
import { IPageConfig } from '../PageConfig';
import SideBar from './SideBar';

export async function loader({request}: {request: Request}): Promise<IPageConfig> {
    await api.init();
    if (!api.isAuthenticated) {
        throw redirect('/login');
    }
    const url = new URL(request.url);
    const view = url.searchParams.get('view');
    let group_id = undefined;
    const s_group_id = url.searchParams.get('group');
    if (s_group_id)
        group_id = +s_group_id;

    let params = {app: 'todo'};
    if (view)
        params = Object.assign(params, {view: view});
    if (group_id)
        params = Object.assign(params, {group: group_id});
    const data = await api.get('config', params);
    const config = new IPageConfig(Object.assign({}, data));
    return config;
}
  
function TodoPage() {
    const [width, setWindowWidth] = useState(window.innerWidth);

    useEffect( () => {
        updateDimensions();
        window.addEventListener("resize", updateDimensions);
        return () => window.removeEventListener("resize", updateDimensions);
    }, []);

    const updateDimensions = () => {
        const width = window.innerWidth;
        setWindowWidth(width);
    };

    const isMobile = width < 768;
    let style;
    if (isMobile) {
        style = {
            flexDirection: 'column',
        };
    } else {
        style = {
            flexDirection: 'row',
        };
    }

    const config = useLoaderData() as IPageConfig;

    return (<div className="d-flex bg-body-tertiary pt-2" style={style}>
        <SideBar width={width} config={config} />
        <Outlet context={config} />
    </div>);
}

export default TodoPage;