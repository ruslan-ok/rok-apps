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
} from 'chart.js';
import { Line } from 'react-chartjs-2';

import Spinner from '../Spinner';
import { apiUrl } from '../auth/Auth';

import './Weight.css';
  
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const options = {
    responsive: true,
    interaction: {},
    plugins: {
        legend: {
            display: false,
        },
    },
    elements: {
        point: {
            radius: 0,
        },
    },
};

let data = {
    datasets: [{
        data: null,
        borderColor: 'rgba(255, 99, 132, 1)',
        borderWidth: 1,
        tension: 0.5,
    }]
}

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

function Weight({screenWidth}: {screenWidth: number}) {
    function setPeriodOption(value: string): void {
        setPeriod(value);
        setOption(value);
    }
    
    const [values, setValues] = useState<any>(null);
    const [period, setPeriod] = useState(getOption());
    const [status, setStatus] = useState('init');
    const chartRef = useRef<any>(null);
    useEffect(() => {
        async function getData() {
            setStatus('updating');
            const url = apiUrl + 'api/get_chart_data/?mark=health&version=v2&period=' + period;
            const aaa: RequestCredentials = 'include';
            const options = {
                method: 'GET',
                headers: {'Content-type': 'application/json'},
                credentials: aaa,
            };
            const response = await fetch(url, options);
            if (response.ok) {
                let resp_data = await response.json();
                if (resp_data) {
                    data.datasets[0].data = resp_data.data;
                    setValues(resp_data);
                    setStatus('ready');
                }
            }
        }
        getData();
        const chart = chartRef.current;
        if (chart) {
            chart.update();
        }
    }, [period]);

    const widgetWidth = screenWidth < 600 ? 410 : (screenWidth < 768 ? 500 : 600);
    const widgetHeight = screenWidth < 600 ? 200 : (screenWidth < 768 ? 250 : 300);
    if (status == 'ready') {
        const current = Math.round(values.current).toLocaleString();
        const change = values.change?.toFixed(2).toLocaleString();
        return (
            <div className='widget-container'>
                <div className='widget-content' id='weight'>
                    <div className='title'>
                        <span id='current' className='section'><span>Вес:</span><span className='value'>{current}</span><span>кг</span></span>
                        <span id='change' className='section'><span className='long-text'>Динамика:</span><span className='value'>{change}</span><span>кг</span></span>
                        <span id='period' className='section'>
                            <select name='period' defaultValue={period} onChange={e => setPeriodOption(e.target.value)}>
                                <option value='7d'>неделя</option> 
                                <option value='30d'>месяц</option> 
                                <option value='3m'>3 месяца</option> 
                                <option value='1y'>год</option> 
                                <option value='3y'>3 года</option> 
                                <option value='5y'>5 лет</option> 
                                <option value='10y'>10 лет</option> 
                            </select>
                        </span>
                        <span className='section value'>
                            <input name='new_value' type='text' placeholder='Добавить'></input>
                            <button className='button' type='button'><i className='bi-plus'></i></button>
                        </span>
                    </div>
                    <Line ref={chartRef} options={options} data={data} width={widgetWidth} height={widgetHeight} key={Math.random()}/>
                </div>
            </div>
        );
    } else {
        return <Spinner width={widgetWidth} height={widgetHeight} />;
    }
}
  
export default Weight;
