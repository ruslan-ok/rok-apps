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
import StyledCheckbox from './StyledCheckbox';

import './Currency.css';
  
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
    code: string;
    currentRate: number;
    color: Color;
};

interface Rate {
    date: string;
    rate: number;
};

interface CurrencyRates {
    currencyId: string;
    rates: Rate[];
};

interface WidgetData {
    baseId: string;
    periodId: string;
    currencyList: CurrencyInfo[];
    rates: CurrencyRates[];
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

let data: ChartData = {
    datasets: []
};

function Currency({width, height}: {width: number, height: number}) {
    const initData: WidgetData = {
        baseId: '',
        periodId: '',
        currencyList: [],
        rates: [],
    };
    const [values, setValues] = useState<WidgetData>(initData);
    const [base, setBase] = useState<string>('usd');
    const [period, setPeriod] = useState<string>('7d');
    const [hidden, setHidden] = useState<Array<string>>([]);
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
                    // console.log(resp_data);
                    setBase(resp_data.baseId);
                    setPeriod(resp_data.periodId);
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

    if (status == 'ready') {

        function switchVisible() {
            const currencyList = document.getElementsByClassName('styled-checkbox');
            let hidden: Array<string> = [];
            for (const currency of currencyList) {
                if (!(currency as HTMLInputElement).checked) {
                    hidden.push((currency as HTMLInputElement).name);
                }
            }
            setHidden(hidden);
        }
        
        const currencyList = values.currencyList.map(item => { return (<option key={item.id} value={item.id}>{item.code}</option>); });
        const noBaseList = values.currencyList.filter(x => x.id != base).map(item => {
            const visible = !hidden.includes(item.id);
            return (
                <StyledCheckbox key={item.id} id={item.id} text={item.code} r={item.color.r} g={item.color.g} b={item.color.b} checked={visible} onClick={switchVisible} />
            );
        });
        
        data.datasets = [];
        values.rates.forEach(currencyRates => {
            const currency: CurrencyInfo = values.currencyList.filter(x => x.id == currencyRates.currencyId)[0];
            if (!hidden.includes(currency.id)) {
                const currInfo: DatasetInfo = {
                    label: currency.code,
                    data: currencyRates.rates,
                    backgroundColor: `rgba(${currency.color.r}, ${currency.color.g}, ${currency.color.b}, 0.2)`,
                    borderColor: `rgba(${currency.color.r}, ${currency.color.g}, ${currency.color.b}, 1)`,
                    borderWidth: 1,
                    tension: 0.4,
                };
                data.datasets.push(currInfo);
            }
        });
        // console.log(data);

        // console.log(options);
        return (
            <div className='widget'>
                <div className='title'>
                    <span id='base-curr' className='section'>
                        <select name='base-curr' defaultValue={base} onChange={e => setBase(e.target.value)}>
                            {currencyList}
                        </select>
                    </span>
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
                    {noBaseList}
                </div>
                <Line ref={chartRef} options={options} data={data} width={width} height={height} key={Math.random()}/>
            </div>
        );
    } else {
        return <Spinner />;
    }
}
  
export default Currency;
