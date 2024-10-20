import { redirect, useLoaderData, Outlet } from "react-router-dom";
import { api } from '../../API'
import { IPageConfig } from '../PageConfig';
import SideBarTop from './SideBarTop';
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
    const data: IPageConfig = await api.get('config', params);
    return data;
}
  
function TodoPage() {
    const config = useLoaderData() as IPageConfig;
    return (
        <>
            <SideBarTop />
            <div className="container-xxl my-md-2 gap-0 px-0 bd-layout">
                <SideBar config={config} />
                <Outlet context={config} />
            </div>
        </>
    );
}
  
export default TodoPage;