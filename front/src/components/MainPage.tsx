import type { LoaderFunctionArgs } from "react-router-dom";
import { useLoaderData } from "react-router-dom";
import { auth, apiUrl } from './auth/Auth';
import type { PublicData } from './MainPagePublic';
import MainPagePublic from './MainPagePublic';
import MainPageProtected from './MainPageProtected';
import MainPageSearch from './MainPageSearch';

export interface MainPageData {
  publicData: PublicData;
  searchString: string|null;
}

export async function loader({ request }: LoaderFunctionArgs): Promise<MainPageData> {
  const cred: RequestCredentials = 'include';
  const url = new URL(request.url);
  const searchString = url.searchParams.get("q");
  const options = { 
    method: 'GET', 
    headers: { 
      'Content-type': 'application/json'
    },
    credentials: cred,
  };
  const res = await fetch(apiUrl +  'api/react/main_page/', options);
  const resp_data = await res.json();
  const publicData = JSON.parse(resp_data.json_data);
  const data: MainPageData = {
    publicData: publicData,
    searchString: searchString,
  };
  return data;
}

function MainPage() {
  const data: MainPageData = useLoaderData() as MainPageData;
  let layout;
  if (auth.isAuthenticated) {
    if (data.searchString) {
      layout = <MainPageSearch searchString={data.searchString}/>;
    } else {
      layout = <MainPageProtected />;
    }
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