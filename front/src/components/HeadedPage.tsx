import { useState, useEffect } from 'react';
import { Outlet } from "react-router-dom";
  
import { AuthProvider, appAuthProvider, apiUrl, getAccessToken } from './Auth';
import type { HeaderData } from './header/Header';
import Header from './header/Header';

export interface AppData {
    auth: AuthProvider;
    header: HeaderData;
};
  
export async function loader(): Promise<HeaderData> {
    const auth: AuthProvider = await appAuthProvider.init();
    // console.log(auth);
    const token = getAccessToken();
    const options = { 
        method: 'GET', 
        headers: { 
        'Content-type': 'application/json'
        } 
    };
    const res = await fetch(apiUrl +  'api/react/header?userToken=' + token, options);
    const resp_data = await res.json();
    const header: HeaderData = JSON.parse(resp_data.json_data);
    // console.log(header);
    const data: AppData = {
        auth: auth,
        header: header
    };

    // @ts-ignore
    return data;
}
  
function HeadedPage() {
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

    return (
        <>
            <Header windowWidth={width} />
            <Outlet />
        </>
    );
}
  
export default HeadedPage;