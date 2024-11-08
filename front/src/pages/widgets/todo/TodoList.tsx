import { useState, useEffect } from 'react';
import { api } from '../../../API'
import SubGroup, { IWidgetSubGroup, buildSubGroupList } from './SubGroup';
import WidgetContainer from '../WidgetContainer';


export default function TodoList() {
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

    let subGroupList;
    if (status === 'ready') {
        const subGroups: IWidgetSubGroup[] = buildSubGroupList(values.data);
        subGroupList = subGroups.map((sg: IWidgetSubGroup) => {
            return (<SubGroup key={sg.id} data={sg} doRedraw={doRedraw}/>);
        });
    }
    return (
        <WidgetContainer name={"Weather"} status={status} message={message} >
            {status === 'ready' &&
                <div className='widget-content'> 
                    <h5 className="">{values.title}</h5>
                    <div className='todo-list'>
                        {subGroupList}
                    </div>
                </div>
            }
        </WidgetContainer>
    );
}