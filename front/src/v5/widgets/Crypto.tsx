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

import Spinner from 'react-bootstrap/Spinner';

import { api } from '../../API'
import { Container } from 'react-bootstrap';

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

function Crypto() {
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

    if (status === 'ready') {
        const current = Math.round(widgetData.current).toLocaleString();
        const change = widgetData.change;
        let changeClass = 'ms-2';
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
            <Container style={{maxWidth: '600px'}}>
                <div className='widget-container'>
                    <div className='widget-content' id='crypto'> 
                        <div className='title'>
                            <a className='d-flex' href={price_url}><i className='bi-currency-bitcoin me-2'></i><span className='value'>${current}</span></a>
                            <span className='d-flex'>Динамика:<span className={changeClass}>{change}</span> %</span>
                            <a className='d-flex' href={amount_url}><i className='bi-wallet2 me-2'></i><span className='value'>${amount}</span></a>
                            <span className='d-flex'>
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
                        <Line ref={chartRef} options={widgetData.chart.options} data={widgetData.chart.data} key={Math.random()}/>
                    </div>
                </div>
            </Container>
        );
    } else {
        return (
            <Container className="d-flex justify-content-center align-items-center" style={{maxWidth: '600px', minHeight: '200px'}}>
                <Spinner animation="border" role="status" variant="secondary">
                    <span className="visually-hidden">Loading...</span>
                </Spinner>
            </Container>
        );
    }

}
  
export default Crypto;
