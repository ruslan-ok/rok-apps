import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { auth as api} from './Auth';

function Logout() {
    const navigate = useNavigate();

    useEffect(() => {
        async function action() {
            await api.logout();
            navigate('/');
        }
        
        action();
    }, [navigate]);
    return (<></>);
}

export default Logout;
