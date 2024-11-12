import { useState, useEffect } from "react";
import Accordion from 'react-bootstrap/Accordion';
import { api } from '../API'
import { Container } from "react-bootstrap";


interface IApplicationDescr {
    app_id: string;
    icon: string;
    title: string;
    features: string[];
}

interface IMainPage {
    applications: IApplicationDescr[];
}

function MainPagePublic() {
    const [data, setData] = useState<IMainPage>({applications: []});
    useEffect(() => {
        const getData = async () => {
            const data: IMainPage = await api.free_get('main_page', {});
            setData(data);
        };
      
        getData();
    }, []);

    const items = data.applications.map(item => {
        const iconClass = 'bi-' + item.icon + ' me-2';
        return (
            <Container key={item.app_id} >
                <Accordion.Item eventKey={item.app_id}>
                    <Accordion.Header><i className={iconClass} />{item.app_id}</Accordion.Header>
                    <Accordion.Body>
                        <p>{item.title}</p>
                        <ul>
                            {item.features.map((cli, i) => { return (<li key={i}>{cli}</li>) })}
                        </ul>
                    </Accordion.Body>
                </Accordion.Item>
            </Container>
        );
    });
    return <Accordion defaultActiveKey="0" className="pt-2">
        {items}
    </Accordion>;
}

export default MainPagePublic;
