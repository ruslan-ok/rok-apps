import { redirect, useLoaderData } from "react-router-dom";
import { auth, apiUrl } from '../auth/Auth';
import SideBarTop from './SideBarTop';
import SideBar from './SideBar';
import TodoContent from './TodoContent';

interface GroupPathInfo {
    id: number;
    name: string;
    edit_url: string;
}

interface RoleInfo {
    name: string;
    href: string;
    icon: string;
}

interface SortInfo {
    id: number;
    name: string;
}

interface ThemeInfo {
    id: number;
    img: string | null;
    style: string | null;
}

interface SubGroupInfo {
    id: number;
    name: string;
    is_open: boolean;
}

export interface PageConfigInfo {
    app: string;
    role: string;
    title: string;
    entity: string;
    icon: string;
    group_path: Array<GroupPathInfo>;
    group_return: number;
    add_item_placeholder: string;
    theme_id: number;
    dark_theme: boolean;
    use_sub_groups: boolean;
    grp_use_sub_groups: boolean;
    sort_id: string;
    sort_reverse: boolean;
    sort_name: string;
    sorts: Array<SortInfo>;
    view: string | undefined;
    group_id: number | undefined;
    item_id: number | undefined;
    theme: string;
    use_groups: boolean;
    folder: string;
    path: string;
    related_roles: Array<RoleInfo>;
    possible_related: Array<RoleInfo>;
    hide_add_item_input: boolean;
    themes: Array<ThemeInfo>;
    grp_view_id: string;
    grp_services_visible: boolean;
    sub_groups: Array<SubGroupInfo> | undefined;
    cur_view_group_id: number | undefined;
    use_selector: boolean;
    use_important: boolean;
    event_in_name: boolean;
    determinator: string | undefined;
}
  
export async function loader({request}: {request: Request}): Promise<PageConfigInfo> {
    await auth.init();
    if (!auth.isAuthenticated) {
        throw redirect('/login');
    }
    const cred: RequestCredentials = 'include';
    const headers =  {'Content-type': 'application/json'};
    const options = { 
      method: 'GET', 
      headers: headers,
      credentials: cred,
    };
    const url = new URL(request.url);
    const view = url.searchParams.get('view');
    const group_id = url.searchParams.get('group');
    const params = '?format=json&app=todo' + (view ? `&view=${view}` : group_id ? `&group=${group_id}` : '');
    const res = await fetch(apiUrl +  'api/env/' + params, options);
    const resp_data = await res.json();
    return Object.assign(resp_data, {
        app: 'todo', 
        role: 'todo', 
        view: view, 
        group_id: group_id, 
        entity: 'group',
        use_groups: true,
    });
}
  
function TodoPage() {
    const config = useLoaderData() as PageConfigInfo;
    return (
        <>
            <SideBarTop />
            <div className="container-xxl my-md-2 gap-0 px-0 bd-layout">
                <SideBar config={config}/>
                <TodoContent config={config}/>
            </div>
        </>
    );
}
  
export default TodoPage;