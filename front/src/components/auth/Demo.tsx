import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { auth } from './Auth';

function Demo() {
    const navigate = useNavigate();

    useEffect(() => {
        async function action() {
            await auth.demo();
            navigate('/react');
        }
        
        action();
    }, []);
    return (<></>);
}

export default Demo;