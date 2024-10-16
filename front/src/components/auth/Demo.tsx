import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { auth as api } from './Auth';

function Demo() {
    const navigate = useNavigate();

    useEffect(() => {
        async function action() {
            await api.demo();
            navigate('/');
        }
        
        action();
    }, [navigate]);
    return (<></>);
}

export default Demo;
