import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { auth } from './Auth';

function Logout() {
    const navigate = useNavigate();

    useEffect(() => {
        async function action() {
            await auth.logout();
            navigate('/');
        }
        
        action();
    }, []);
    return (<></>);
}

export default Logout;