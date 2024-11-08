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

import { api } from '../../API'
import StyledCheckbox from './StyledCheckbox';
import WidgetContainer from './WidgetContainer';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

type Color = {
    r: number,
    g: number,
    b: number,
};

interface ICurrency {
    id: string;
    rate: number;
    rates: number[];
    color: Color;
};

interface IRate {
    x: string;
    y: number;
};

interface IWidget {
    chart: any;
    base: string;
    period: string;
    labels: string[];
    currencies: ICurrency[];
};


interface IDataset {
    label: string;
    data: IRate[];
    backgroundColor: string;
    borderColor: string;
    borderWidth: number;
    tension: number;
};

interface IChart {
    datasets: IDataset[];
}

let chartData: IChart = {
    datasets: []
};

function getOption(kind: string): string {
    const tmp: string | null = localStorage.getItem('currency-' + kind);
    let ret: string = '';
    if (tmp != null) {
        ret = tmp;
    } else {
        switch (kind) {
            case 'base':
                ret = 'usd';
                break;
            case 'period':
                ret = '7d';
                break;
            case 'hidden':
                ret = '';
                break;
        }
    }
    return ret;
}

function setOption(kind: string, value: string): void {
    localStorage.setItem('currency-' + kind, value);
}

function Currency() {

    function setBaseOption(value: string): void {
        setBase(value);
        setOption('base', value);
    }
    
    function setPeriodOption(value: string): void {
        setPeriod(value);
        setOption('period', value);
    }
    
    function setHiddenOption(values: string[]): void {
        setHidden(values);
        setOption('hidden', values.join(','));
    }
    
    function switchVisible() {
        const currencies = document.getElementsByClassName('styled-checkbox');
        let hidden: Array<string> = [];
        for (const currency of currencies) {
            if (!(currency as HTMLInputElement).checked) {
                hidden.push((currency as HTMLInputElement).name);
            }
        }
        setHiddenOption(hidden);
    }
    
    const initData: IWidget = {
        chart: {},
        base: '',
        period: '',
        labels: [],
        currencies: [],
    };

    const [widgetData, setWidgetData] = useState<IWidget>(initData);
    const [base, setBase] = useState<string>(getOption('base'));
    const [period, setPeriod] = useState<string>(getOption('period'));
    const [hidden, setHidden] = useState<Array<string>>(getOption('hidden').split(','));
    const [status, setStatus] = useState('init');
    const chartRef = useRef<any>(null);

    useEffect(() => {
        async function getData() {
            setStatus('updating');
            let widgetData = await api.get('chart', {mark: 'currency', version: 'v2', period: period, base: base});
            if (widgetData) {
                setWidgetData(widgetData);
                setBaseOption(widgetData.base);
                setPeriodOption(widgetData.period);
                setStatus('ready');
            }
        }
        getData();
        const chart = chartRef.current;
        if (chart) {
            chart.update();
        }
    }, [period, base]);

    let currencies;
    let noBaseList;
    if (status === 'ready') {
        currencies = widgetData.currencies.map(item => { return (<option key={item.id} value={item.id}>{item.id.toUpperCase()}</option>); });
        noBaseList = widgetData.currencies.filter(x => x.id !== base).map(item => {
            const visible = !hidden.includes(item.id);
            return (
                <StyledCheckbox classes='visibility' key={item.id} id={item.id} text={item.id.toUpperCase()} r={item.color.r} g={item.color.g} b={item.color.b} checked={visible} onClick={switchVisible} />
            );
        });
        
        chartData.datasets = [];
        widgetData.currencies.filter(x => x.id !== base && !hidden.includes(x.id)).forEach(currency => {
            const currInfo: IDataset = {
                label: currency.id.toUpperCase(),
                data: currency.rates.map((rate, index) => { return {x: widgetData.labels[index], y: rate } }),
                backgroundColor: `rgba(${currency.color.r}, ${currency.color.g}, ${currency.color.b}, 0.2)`,
                borderColor: `rgba(${currency.color.r}, ${currency.color.g}, ${currency.color.b}, 1)`,
                borderWidth: 1,
                tension: 0.4,
            };
            chartData.datasets.push(currInfo);
        });
    }

    return (
        <WidgetContainer name={"Currency"} status={status} message={""} >
            <div className='widget-content' id='currency'>
                <div className='bg-primary-subtle p-2 d-flex align-items-center justify-content-around'>
                    <span className='section base-curr' style={{maxWidth: '70px'}}>
                        <select name='base-curr' defaultValue={base} onChange={e => setBaseOption(e.target.value)} className="form-select" >
                            {currencies}
                        </select>
                    </span>
                    <span className='section period' style={{maxWidth: '100px'}}>
                        <select name='period' defaultValue={period} onChange={e => setPeriodOption(e.target.value)}  className="form-select">
                            <option value='7d'>неделя</option> 
                            <option value='30d'>месяц</option> 
                            <option value='3m'>3 месяца</option> 
                            <option value='1y'>год</option> 
                            <option value='3y'>3 года</option> 
                            <option value='5y'>5 лет</option> 
                            <option value='10y'>10 лет</option> 
                        </select>
                    </span>
                    {noBaseList}
                </div>
                <Line ref={chartRef} options={widgetData.chart.options} data={chartData} key={Math.random()}/>
            </div>
        </WidgetContainer>
    );

}
  
export default Currency;
