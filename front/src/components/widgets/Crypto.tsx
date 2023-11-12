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

import './Crypto.css';
  
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
        borderColor: 'rgba(111, 184, 71, 1)',
        borderWidth: 1,
        tension: 0.5,
    }]
}

function getOption(): string {
    const tmp: string | null = localStorage.getItem('crypto-period');
    let ret: string = '7d';
    if (tmp != null) {
        ret = tmp;
    }
    return ret;
}

function Crypto({screenWidth}: {screenWidth: number}) {
    function setPeriodOption(value: string): void {
        setPeriod(value);
        localStorage.setItem('crypto-period', value);
    }
    
    const [values, setValues] = useState<any>(null);
    const [period, setPeriod] = useState(getOption());
    const [status, setStatus] = useState('init');
    const chartRef = useRef<any>(null);

    useEffect(() => {
        async function getData() {
            setStatus('updating');
            const url = apiUrl + 'api/get_chart_data/?mark=crypto&version=v2&period=' + period;
            const cred: RequestCredentials = 'include';
            const options = {
                method: 'GET',
                headers: {'Content-type': 'application/json'},
                credentials: cred,
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
        const change = values.change;
        let changeClass = 'value';
        if (change > 0) {
            changeClass += ' posotive';
        }
        if (change < 0) {
            changeClass += ' negative';
        }
        const amount = Math.round(values.amount).toLocaleString();
        const price_url = values.price_url;
        const amount_url = values.amount_url;
            return (
            <div className='widget-container'>
                <div className='widget-content' id='crypto'> 
                    <div className='title'>
                        <a className='section current' href={price_url}><i className='bi-currency-bitcoin icon'></i><span className='value'>${current}</span></a>
                        <span className='section change'>Динамика:<span className={changeClass}>{change}</span> %</span>
                        <a className='section amount' href={amount_url}><i className='bi-wallet2 icon'></i><span className='value'>${amount}</span></a>
                        <span className='section period'>
                            <select name='period' defaultValue={period} onChange={e => setPeriodOption(e.target.value)}>
                                <option value='1h'>1 час</option> 
                                <option value='3h'>3 часа</option> 
                                <option value='12h'>12 часов</option> 
                                <option value='24h'>сутки</option> 
                                <option value='7d'>неделя</option> 
                                <option value='30d'>месяц</option> 
                                <option value='3m'>3 месяца</option> 
                                <option value='1y'>год</option> 
                                <option value='3y'>3 года</option> 
                                <option value='5y'>5 лет</option> 
                            </select>
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
  
export default Crypto;
