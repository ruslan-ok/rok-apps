import { useState, useEffect } from 'react';
import { Outlet } from "react-router-dom";
  
import { auth, apiUrl } from './auth/Auth';
import type { HeaderData } from './header/Header';
import Header from './header/Header';

export async function loader(): Promise<HeaderData> {
    await auth.init();
    const cred: RequestCredentials = 'include';
    const options = { 
        method: 'GET', 
        headers: { 
        'Content-type': 'application/json'
        },
        credentials: cred,
    };
    const res = await fetch(apiUrl +  'api/react/header', options);
    const resp_data = await res.json();
    const header: HeaderData = JSON.parse(resp_data.json_data);
    return header;
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