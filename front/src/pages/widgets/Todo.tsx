import { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import { api } from '../../API'
import WidgetContainer from './WidgetContainer';
import type { ISubGroup } from '../todo/SubGroup';
import SubGroup, { fillSubGroups } from '../todo/SubGroup';
import { IItemInfo } from '../todo/ItemTypes';
import { IPageConfig } from '../PageConfig';


export default function Todo() {
    const [status, setStatus] = useState('init');
    const [redraw, setRedraw] = useState('1');
    const [subGroups, setData] = useState<ISubGroup[]>([]);

    function compareSG(a: ISubGroup, b: ISubGroup): number {
        return a.id - b.id;
    }

    useEffect(() => {
        async function getData() {
            setStatus('loading');
            let params = {view: 'widget'};
            const data: IItemInfo[] = await api.get('todo', params);
            const items = data.map(x => {return new IItemInfo(x);});
            const sgList: ISubGroup[] = fillSubGroups(items, 0, true);
            const validSG = sgList.filter(x => x.items.length).sort(compareSG);
            setData(validSG);
            setStatus('ready');
        }

        getData();
    }, [redraw])

    function doRedraw() {
        setRedraw(redraw === '0' ? '1' : '0');
    }

    const configData = {
        title: 'Actual tasks',
        icon: '"check2-square"',
        event_in_name: false,
        use_groups: null,
        use_selector: true,
        use_star: true,
        add_item: null,
        related_roles: [],
        possible_related: [],
        entity: {
            id: null,
            name: 'group',
            path: [],
        },
        sorts: [
            {
                id: 'stop',
                name: 'Termin',
            },
        ],
        themes: [
            {
                id: 8,
                style: 'theme-8',
            },
        ],
        theme_id: 8,
        view_group: {
            id: 0,
            name: "Actual tasks",
            app: "todo",
            role: "todo",
            theme: 8,
            use_sub_groups: true,
            act_items_qty: 0,
            sub_groups: "[]",
            determinator: "view",
            view_id: "widget",
            items_sort: "stop"
        }
    };

    const config = new IPageConfig(configData);

    let sgList;
    if (status === 'ready' && subGroups.length) {
        sgList = subGroups.map(x => { return <SubGroup key={x.id} subGroup={x} config={config} update={doRedraw} /> });
    } else {
        sgList = <></>;
    }

    const style = {
        height: '39px',
        paddingTop: '8px',
        paddingLeft: '16px',
        margin: '0',
    }
    return (
        <Container style={{maxWidth: '600px', minHeight: '200px', }} className="bg-white p-0 mb-3 align-self-start" >
            <h6 className="bg-primary-subtle" style={style} >{config.title}</h6>
            <WidgetContainer status={status} message={''} >
                {status === 'ready' &&
                    <div className='widget-content'> 
                        <div className='todo-list'>
                            {sgList}
                        </div>
                    </div>
                }
            </WidgetContainer>
        </Container>
    );
}