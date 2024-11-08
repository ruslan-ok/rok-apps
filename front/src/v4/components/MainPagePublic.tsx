import { useState, useEffect } from "react";
import { api } from '../API';

interface IApplicationDescr {
    app_id: string;
    icon: string;
    title: string;
    features: string[];
}

interface IMainPage {
    applications: IApplicationDescr[];
}

interface IParsedApp {
    id: string,
    title: string,
    heading_id: string,
    collapse_id: string,
    hash_collapse_id: string,
    icon_class: string,
    button_class: string,
    expanded: boolean,
    data_class: string,
    features: string[],
}

function MainPagePublic() {
    const [data, setData] = useState<IMainPage>([]);
    useEffect(() => {
        const getData = async () => {
            const data: IMainPage = await api.free_get('main_page', {});
            setData(data);
        };
      
        getData();
    }, []);

    let dataExt: IParsedApp[] = [];

    if (data && data.applications?.length) {
        dataExt = data.applications.map((item, index) => {
            return {
                id: item.app_id,
                title: item.title,
                heading_id: 'heading' + item.app_id,
                collapse_id: 'collapse' + item.app_id,
                hash_collapse_id: '#collapse' + item.app_id,
                icon_class: 'bi-' + item.icon + ' me-2',
                button_class: 'accordion-button' + (index ? ' collapsed' : ''),
                expanded: index ? false : true,
                data_class: 'accordion-collapse collapse' + (index ? '' : ' show'),
                features: item.features,
            };
        });
    }

    const listItems = dataExt.map(item => 
        <div className="accordion-item rok-main-page-public" key={item.id}>
            <h2 className="accordion-header" id={item.heading_id}>
                <button className={item.button_class} type="button" data-bs-toggle="collapse" data-bs-target={item.hash_collapse_id} aria-expanded={item.expanded} aria-controls={item.collapse_id}>
                    <i className={item.icon_class}></i>
                    {item.id}
                </button>
            </h2>
            <div id={item.collapse_id} className={item.data_class} aria-labelledby={item.heading_id} data-bs-parent="#accordeonIntro">
                <div className="accordion-body">
                    <p>{item.title}</p>
                    <ul>
                    {item.features.map((cli, i) => { return (<li key={i}>{cli}</li>) })}
                    </ul>
                </div>
            </div>
        </div>
    );

    return (
        <main>
            <div className='content p-2'>
                <p className="lead">This site provides the following functionality:</p>

                <div className="accordion" id="accordeonIntro">
                    {listItems}
                </div>

                <div className="d-flex mt-4">
                    <div className="lead">
                        Try demo-mode without registration:
                    </div>
                    <a href="{% url 'account:demo' %}" className="btn btn-secondary mx-3">Demo</a>
                </div>
            </div>
        </main>
    );
}

export default MainPagePublic;