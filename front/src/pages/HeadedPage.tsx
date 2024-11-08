import { Outlet } from "react-router-dom";
import Header from './Header';

function HeadedPage() {
    return (
        <>
            <Header />
            <Outlet />
        </>
    );
}
  
export default HeadedPage;