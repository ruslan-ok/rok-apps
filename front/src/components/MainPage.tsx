import { useState, useEffect } from 'react';
import {
  useRouteLoaderData,
} from "react-router-dom";

import { apiUrl, getAccessToken } from './Auth';
import type { AuthProvider } from './Auth';
import type { HeaderData } from './header/Header';
import type { PublicData } from './MainPagePublic';
import type { ProtectedData } from './MainPageProtected';
import MainPagePublic from './MainPagePublic';
import MainPageProtected from './MainPageProtected';

export interface MainPageData {
  headerData: HeaderData;
  publicData: PublicData;
  protectedData: ProtectedData;
}

export async function loader(): Promise<MainPageData> {
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
  const [width, setWindowWidth] = useState(0);

  useEffect( () => {
    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  const updateDimensions = () => {
    const width = window.innerWidth;
    setWindowWidth(width);
  };

  const responsive = {
    windowWidth: width
  };

  let auth = useRouteLoaderData('root') as AuthProvider;

  if (!auth.isAuthenticated) {
    return <MainPagePublic windowWidth={responsive.windowWidth} />;
  }
  return <MainPageProtected windowWidth={responsive.windowWidth} />;
}
  
export default MainPage;  