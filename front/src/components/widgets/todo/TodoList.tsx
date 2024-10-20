import { useState, useEffect } from 'react';
import Spinner from '../../Spinner';
import { api } from '../../../API'
import SubGroup, { SubGroupInfo, buildSubGroupList } from './SubGroup';

import './TodoList.css';

export default function TodoList({screenWidth}: {screenWidth: number}) {
    const [status, setStatus] = useState('init');
    const [values, setValues] = useState<any>(null);
    const [message, setMessage] = useState('');
    const [redraw, setRedraw] = useState('1');

    useEffect(() => {
        async function getData() {
            setStatus('updating');
            let resp_data = await api.get('chart', {mark: 'todo'});
            if (resp_data) {
                setValues(resp_data);
                if (resp_data.result === 'ok') {
                    setStatus('ready');
                }
                else {
                    setStatus('mess');
                    setMessage(resp_data.procedure + ': ' + resp_data.info);
                }
            }
        }

        getData();
    }, [redraw])

    function doRedraw() {
        setRedraw(redraw === '0' ? '1' : '0');
    }

    const widgetWidth = screenWidth < 600 ? 410 : (screenWidth < 768 ? 500 : 600);
    const widgetHeight = screenWidth < 600 ? 200 : (screenWidth < 768 ? 250 : 300);

    if (status !== 'ready' && status !== 'mess') {
        return <Spinner width={widgetWidth} height={widgetHeight} />;
    } else
        if (status === 'mess') {
            return <p>{message}</p>;
        } else {
            const subGroups: SubGroupInfo[] = buildSubGroupList(values.data);
            const subGroupList = subGroups.map((sg: SubGroupInfo) => {
                return (<SubGroup key={sg.id} data={sg} doRedraw={doRedraw}/>);
            });

            return (
                <div className='widget-container' id='todo-list'>
                    <div className='widget-content'> 
                        <h5 className="">{values.title}</h5>
                        <div className='todo-list'>
                            {subGroupList}
                        </div>
                    </div>
                </div>
            );
        }
}