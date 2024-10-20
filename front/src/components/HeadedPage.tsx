import { useState, useEffect } from 'react';
import { Outlet } from "react-router-dom";
  
import { api } from '../API'
import type { HeaderData } from './header/Header';
import Header from './header/Header';

export async function loader(): Promise<HeaderData> {
    await api.init();
    return await api.get('header', {});
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