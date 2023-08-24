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
import { apiUrl } from '../Auth';

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

  
function Weight() {
    const [values, setValues] = useState<any>(null);
    const [period, setPeriod] = useState('30d');
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
                    //console.log(data);
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

    if (status == 'ready') {
        const current = Math.round(values.current).toLocaleString();
        const change = values.change?.toFixed(2).toLocaleString();
        return (
            <div className='widget'>
                <div className='title'>
                    <span id='current' className='section'><span>Вес:</span><span className='value'>{current}</span><span>кг</span></span>
                    <span id='change' className='section'><span>Динамика:</span><span className='value'>{change}</span><span>кг</span></span>
                    <span id='period' className='section'>
                        <select name='period' defaultValue={period} onChange={e => setPeriod(e.target.value)}>
                            <option value='7d'>неделя</option> 
                            <option value='30d'>месяц</option> 
                            <option value='3m'>3 месяца</option> 
                            <option value='1y'>год</option> 
                            <option value='3y'>3 года</option> 
                            <option value='5y'>5 лет</option> 
                            <option value='10y'>10 лет</option> 
                        </select>
                    </span>
                </div>
                <Line ref={chartRef} options={options} data={data} width={500} height={300} key={Math.random()}/>
            </div>
        );
    } else {
        return <Spinner />;
    }
}
  
export default Weight;
