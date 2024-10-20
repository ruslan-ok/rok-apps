import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from '../../API'

function Logout() {
    const navigate = useNavigate();

    useEffect(() => {
        async function action() {
            const resp = await api.get('logout', {});
            if (resp && resp.ok) {
                api.isAuthenticated = false;
                api.username = '';
            }
            navigate('/');
        }
        
        action();
    }, [navigate]);
    return (<></>);
}

export default Logout;
