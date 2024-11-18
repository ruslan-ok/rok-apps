import { useState, useEffect, useRef } from 'react';
import { Container } from 'react-bootstrap';

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

import WidgetContainer, { IChart } from './WidgetContainer';
import { api } from '../../API'

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

class TCrypto {
    chart: IChart;
    current: number;
    change: number;
    amount: number;
    price_url: string;
    amount_url: string;

    constructor (data: Object | unknown) {
        this.chart = data?.chart;
        this.current = data?.current || 0;
        this.change = data?.change || 0;
        this.amount = data?.amount;
        this.price_url = data?.price_url;
        this.amount_url = data?.amount_url;
    }
}

function Crypto() {
    function setPeriodOption(value: string): void {
        setPeriod(value);
        localStorage.setItem('crypto-period', value);
    }
    
    const [widgetData, setWidgetData] = useState<TCrypto|null>(null);
    const [period, setPeriod] = useState(getOption());
    const [status, setStatus] = useState('init');
    const [message, setMessage] = useState('');
    const chartRef = useRef<any>(null);

    useEffect(() => {
        async function getData() {
            setStatus('loading');
            let widgetData = await api.get('chart', {mark: 'crypto', version: 'v2', period: period});
            if (widgetData) {
                const cryptoData = new TCrypto(widgetData);
                if (!cryptoData.current) {
                    setMessage('Bad Crypto Widget responce');
                    setStatus('message');
                } else {
                    setWidgetData(cryptoData);
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

    let change, current, amount, price_url, amount_url, changeStyle;
    if (status === 'ready' && widgetData) {
        current = Math.round(widgetData.current).toLocaleString();
        change = widgetData.change;
        if (change > 0) {
            changeStyle = {color: 'green'};
        }
        if (change < 0) {
            changeStyle = {color: 'red'};
        }
        amount = Math.round(widgetData.amount).toLocaleString();
        price_url = widgetData.price_url;
        amount_url = widgetData.amount_url;
    }
    return (
        <Container style={{maxWidth: '600px', minHeight: '200px', }} className="bg-white p-0 mb-3 align-self-start" id='crypto' >
            <div className='bg-success-subtle p-1 d-flex align-items-center justify-content-around'>
                <a className='d-flex' href={price_url}><i className='bi-currency-bitcoin me-2'></i><span className='value'>${current}</span></a>
                <span className='d-flex'>Динамика:<span className="px-2" style={changeStyle}>{change}</span> %</span>
                <a className='d-flex' href={amount_url}><i className='bi-wallet2 me-2'></i><span className='value'>${amount}</span></a>
                <span className='d-flex'>
                    <select name='period' defaultValue={period} onChange={e => setPeriodOption(e.target.value)} className="form-select form-select-sm" >
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
            <WidgetContainer status={status} message={message} >
                {status === 'ready' && widgetData &&
                    <Line ref={chartRef} options={widgetData.chart.options} data={widgetData.chart.data} key={Math.random()}/>
                }
            </WidgetContainer>
        </Container>
    );
}
  
export default Crypto;
