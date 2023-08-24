import { useRouteLoaderData } from 'react-router-dom';

import { appAuthProvider as auth, apiUrl, getAccessToken } from './Auth';
import type { AppData } from './HeadedPage';
import type { PublicData } from './MainPagePublic';
import type { ProtectedData } from './MainPageProtected';
import MainPagePublic from './MainPagePublic';
import MainPageProtected from './MainPageProtected';

export interface MainPageData {
  publicData: PublicData;
  protectedData: ProtectedData;
}

export async function loader(): Promise<MainPageData> {
  auth.init();
  const token = getAccessToken();
  const options = { 
    method: 'GET', 
    headers: { 
      'Content-type': 'application/json'
    } 
  };
  const res = await fetch(apiUrl +  'api/react/main_page?userToken=' + token, options);
  const resp_data = await res.json();
  const data: MainPageData = JSON.parse(resp_data.json_data);
  return data;
}

function MainPage() {
  const data = useRouteLoaderData('root') as AppData;

  let layout;
  if (data.auth.isAuthenticated) {
    layout = <MainPageProtected />;
  } else {
    layout = <MainPagePublic />;
  }

  return (
    <>
      {layout}
    </>
  );
}
  
export default MainPage;  