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

import Spinner from '../Spinner';
import { auth as api } from '../auth/Auth';

import './Crypto.css';
  
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend, 
    TimeScale
);

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
    
    const [widgetData, setWidgetData] = useState<any>(null);
    const [period, setPeriod] = useState(getOption());
    const [status, setStatus] = useState('init');
    const chartRef = useRef<any>(null);

    useEffect(() => {
        async function getData() {
            setStatus('updating');
            let widgetData = await api.get('chart', {mark: 'crypto', version: 'v2', period: period});
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
    }, [period]);

    const widgetWidth = screenWidth < 600 ? 410 : (screenWidth < 768 ? 500 : 600);
    const widgetHeight = screenWidth < 600 ? 200 : (screenWidth < 768 ? 250 : 300);

    if (status === 'ready') {
        const current = Math.round(widgetData.current).toLocaleString();
        const change = widgetData.change;
        let changeClass = 'value';
        if (change > 0) {
            changeClass += ' posotive';
        }
        if (change < 0) {
            changeClass += ' negative';
        }
        const amount = Math.round(widgetData.amount).toLocaleString();
        const price_url = widgetData.price_url;
        const amount_url = widgetData.amount_url;
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
                    <Line ref={chartRef} options={widgetData.chart.options} data={widgetData.chart.data} width={widgetWidth} height={widgetHeight} key={Math.random()}/>
                </div>
            </div>
        );
    } else {
        return <Spinner width={widgetWidth} height={widgetHeight} />;
    }
}
  
export default Crypto;
