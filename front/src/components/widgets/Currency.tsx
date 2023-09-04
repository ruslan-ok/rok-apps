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
import StyledCheckbox from './StyledCheckbox';

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

type Color = {
    r: number,
    g: number,
    b: number,
};

interface CurrencyInfo {
    id: string;
    rate: number;
    rates: number[];
    color: Color;
};

interface Rate {
    x: string;
    y: number;
};

interface WidgetData {
    base: string;
    period: string;
    labels: string[];
    currencies: CurrencyInfo[];
};


interface DatasetInfo {
    label: string;
    data: Rate[];
    backgroundColor: string;
    borderColor: string;
    borderWidth: number;
    tension: number;
};

interface ChartData {
    datasets: DatasetInfo[];
}

let chartData: ChartData = {
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

function Currency({screenWidth}: {screenWidth: number}) {

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
    
    const initData: WidgetData = {
        base: '',
        period: '',
        labels: [],
        currencies: [],
    };

    const [values, setValues] = useState<WidgetData>(initData);
    const [base, setBase] = useState<string>(getOption('base'));
    const [period, setPeriod] = useState<string>(getOption('period'));
    const [hidden, setHidden] = useState<Array<string>>(getOption('hidden').split(','));
    const [status, setStatus] = useState('init');
    const chartRef = useRef<any>(null);

    useEffect(() => {
        async function getData() {
            setStatus('updating');
            const url = apiUrl + `api/get_chart_data/?mark=currency&version=v2&period=${period}&base=${base}`;
            const rq: RequestCredentials = 'include';
            const options = {
                method: 'GET',
                headers: {'Content-type': 'application/json'},
                credentials: rq,
            };
            const response = await fetch(url, options);
            if (response.ok) {
                let resp_data: WidgetData = await response.json();
                if (resp_data) {
                    setValues(resp_data);
                    setBaseOption(resp_data.base);
                    setPeriodOption(resp_data.period);
                    setStatus('ready');
                }
            }
        }
        getData();
        const chart = chartRef.current;
        if (chart) {
            chart.update();
        }
    }, [period, base]);

    const widgetWidth = screenWidth < 600 ? 410 : (screenWidth < 768 ? 500 : 600);
    const widgetHeight = screenWidth < 600 ? 200 : (screenWidth < 768 ? 250 : 300);

    if (status == 'ready') {

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
        
        const currencies = values.currencies.map(item => { return (<option key={item.id} value={item.id}>{item.id.toUpperCase()}</option>); });
        const noBaseList = values.currencies.filter(x => x.id != base).map(item => {
            const visible = !hidden.includes(item.id);
            return (
                <StyledCheckbox classes='visibility' key={item.id} id={item.id} text={item.id.toUpperCase()} r={item.color.r} g={item.color.g} b={item.color.b} checked={visible} onClick={switchVisible} />
            );
        });
        
        chartData.datasets = [];
        values.currencies.filter(x => x.id != base && !hidden.includes(x.id)).forEach(currency => {
            const currInfo: DatasetInfo = {
                label: currency.id.toUpperCase(),
                data: currency.rates.map((rate, index) => { return {x: values.labels[index], y: rate } }),
                backgroundColor: `rgba(${currency.color.r}, ${currency.color.g}, ${currency.color.b}, 0.2)`,
                borderColor: `rgba(${currency.color.r}, ${currency.color.g}, ${currency.color.b}, 1)`,
                borderWidth: 1,
                tension: 0.4,
            };
            chartData.datasets.push(currInfo);
        });

        return (
            <div className='widget-container'>
                <div className='widget-content' id='currency'>
                    <div className='title'>
                        <span className='section base-curr'>
                            <select name='base-curr' defaultValue={base} onChange={e => setBaseOption(e.target.value)}>
                                {currencies}
                            </select>
                        </span>
                        <span className='section period'>
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
                        {noBaseList}
                    </div>
                    <Line ref={chartRef} options={options} data={chartData} width={widgetWidth} height={widgetHeight} key={Math.random()}/>
                </div>
            </div>
        );
    } else {
        return <Spinner width={widgetWidth} height={widgetHeight} />;
    }
}
  
export default Currency;
