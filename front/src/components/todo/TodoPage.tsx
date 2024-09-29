import { redirect, useLoaderData } from "react-router-dom";
import { auth, apiUrl } from '../auth/Auth';
import type { SideBarData } from './SideBar';
import SideBarTop from './SideBarTop';
import SideBar from './SideBar';
import TasksPanel from './TasksPanel';
import "../css/TodoPage.min.css";

export interface TodoData {
    sideBarData: SideBarData;
}
  
export async function loader({request}: {request: Object}): Promise<TodoData> {
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
    const group = url.searchParams.get('group');
    const params = view ? `?view=${view}` : group ? `?group=${group}` : '';
    const res = await fetch(apiUrl +  'api/todo/' + params, options);
    const resp_data = await res.json();
    return resp_data;
}
  
function TodoPage() {
    const data = useLoaderData() as TodoData;
    return (
        <>
            <SideBarTop />
            <div className="container-xxl my-md-2 gap-0 px-0 bd-layout">
                <SideBar data={data.sideBarData}/>
                <TasksPanel />
            </div>
        </>
    );
}
  
export default TodoPage;