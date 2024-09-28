import { auth, apiUrl } from './auth/Auth';
import type { PublicData } from './MainPagePublic';
import type { ProtectedData } from './MainPageProtected';
import MainPagePublic from './MainPagePublic';
import MainPageProtected from './MainPageProtected';

export interface MainPageData {
  publicData: PublicData;
  protectedData: ProtectedData;
}

export async function loader(): Promise<MainPageData> {
  const cred: RequestCredentials = 'include';
  const headers =  {'Content-type': 'application/json'};
  const options = { 
    method: 'GET', 
    headers: headers,
    credentials: cred,
  };
  const res = await fetch(apiUrl +  'api/react/main_page/', options);
  const resp_data = await res.json();
  const data: MainPageData = JSON.parse(resp_data.json_data);
  return data;
}

function MainPage() {
  let layout;
  if (auth.isAuthenticated) {
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