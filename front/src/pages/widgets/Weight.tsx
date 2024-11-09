import { useState, useEffect, useRef } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import 'chartjs-adapter-moment';

import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import WidgetContainer from './WidgetContainer';
import { api } from '../../API'

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale,
);

function getOption(): string {
    const tmp: string | null = localStorage.getItem('weight-period');
    let ret: string = '30d';
    if (tmp != null) {
        ret = tmp;
    }
    return ret;
}

function setOption(value: string): void {
    localStorage.setItem('weight-period', value);
}

function Weight() {
    function setPeriodOption(value: string): void {
        setPeriod(value);
        setOption(value);
    }
    
    const [widgetData, setWidgetData] = useState<any>(null);
    const [period, setPeriod] = useState(getOption());
    const [status, setStatus] = useState('init');
    const [redraw, setRedraw] = useState('1');
    const chartRef = useRef<any>(null);
    useEffect(() => {
        async function getData() {
            setStatus('updating');
            let widgetData = await api.get('chart', {mark: 'health', version: 'v2', period: period});
            if (widgetData) {
                setWidgetData(widgetData);
                setStatus('ready');
            }
        }
        getData();
        const chart = chartRef.current;
        if (chart) {
            chart.update();
        }
    }, [period, redraw]);

    function handleSubmit(e: any) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const formJson = Object.fromEntries(formData.entries());
        const newWeight: number = !Number.isNaN(+formJson.weight) ? +formJson.weight : 0;
        console.log(newWeight);
        if (newWeight !== 0)
            saveNewWeight(newWeight);
    }

    async function saveNewWeight(newWeight: number) {
        const value = newWeight.toString();
        let resp_data = await api.get(`tasks/add_item`, {app: 'health', role: 'marker', name: value, group_id: 'health-marker'});
        if (resp_data) {
            setRedraw(redraw === '0' ? '1' : '0');
        }
    }

    let current, change, changeStyle;
    if (status === 'ready') {
        current = Math.round(widgetData.current).toLocaleString();
        change = widgetData.change?.toFixed(2).toLocaleString();
        if (change > 0) {
            changeStyle = {color: 'red'};
        }
        if (change < 0) {
            changeStyle = {color: 'green'};
        }
    }
    return (
        <WidgetContainer name={"Currency"} status={status} message={""} >
            {status === 'ready' &&
                <div className='widget-content' id='weight'>
                    <div className='bg-danger-subtle p-2 d-flex align-items-center justify-content-around'>
                        <span id='current' className='section'><span>Вес:</span><span className='value px-2'>{current}</span><span>кг</span></span>
                        <span id='change' className='section'><span className='long-text'>Динамика:</span><span className="px-2" style={changeStyle} >{change}</span><span>кг</span></span>
                        <span id='period' className='section'>
                            <select name='period' defaultValue={period} onChange={e => setPeriodOption(e.target.value)} className="form-select" >
                                <option value='7d'>неделя</option> 
                                <option value='30d'>месяц</option> 
                                <option value='3m'>3 месяца</option> 
                                <option value='1y'>год</option> 
                                <option value='3y'>3 года</option> 
                                <option value='5y'>5 лет</option> 
                                <option value='10y'>10 лет</option> 
                            </select>
                        </span>
                        <Form id='value' className='d-flex' method="post" onSubmit={handleSubmit} >
                            <Form.Control type="text" placeholder="Weight" name="weight" defaultValue={""} step=".01" size="sm" style={{maxWidth: '70px'}} />
                            <Button variant="light" type="submit" className="bi-plus ms-1" size="sm" />
                        </Form>
                    </div>
                    <Line ref={chartRef} options={widgetData.chart.options} data={widgetData.chart.data} key={Math.random()}/>
                </div>
            }
        </WidgetContainer>
    );
}
  
export default Weight;
