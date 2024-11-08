import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from '../API'


function Demo() {
    const navigate = useNavigate();

    useEffect(() => {
        async function action() {
            const resp = await api.post('demo', {'grant_type': 'password'});
            if (resp && resp.ok && resp.info) {
                api.username = resp.info;
                api.isAuthenticated = true;
            }
            navigate('/');
        }
        
        action();
    }, [navigate]);
    return (<></>);
}

export default Demo;
