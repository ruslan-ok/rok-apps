import { useState, useEffect } from 'react';
import type { TempBarHeight } from './WeatherUtils';
import { getFakeData, getTempBarsInfo, getDayColor, getDayName, getDayDate, getIconHref } from './WeatherUtils';

// import { apiUrl } from '../../auth/Auth';
import Spinner from '../../Spinner';
import './Weather.css';

function Weather({screenWidth}: {screenWidth: number}) {
    const [values, setValues] = useState<any>(null);
    const [status, setStatus] = useState('init');

    useEffect(() => {
        // async function getData() {
        //     setStatus('updating');
        //     const url = apiUrl + 'api/get_chart_data/?mark=weather&version=v2&period=p7d';
        //     const cred: RequestCredentials = 'include';
        //     const options = {
        //         method: 'GET',
        //         headers: {'Content-type': 'application/json'},
        //         credentials: cred,
        //     };
        //     const response = await fetch(url, options);
        //     if (response.ok) {
        //         let resp_data = await response.json();
        //         if (resp_data) {
        //             setValues(resp_data);
        //             setStatus('ready');
        //         }
        //     }
        // }
        // getData();
        const data = getFakeData();
        setValues(data);
        setStatus('ready');
    }, []);

    const widgetWidth = screenWidth < 600 ? 410 : (screenWidth < 768 ? 500 : 600);
    const widgetHeight = screenWidth < 600 ? 200 : (screenWidth < 768 ? 250 : 300);
    if (status == 'ready') {
        const tempBarHeights: TempBarHeight[] = getTempBarsInfo(values.daily.data);
        const days = values.daily.data.map((day: any, index: number) => {
            const color = getDayColor(day.day);
            const clas = 'week-column ' + color;
            const name = getDayName(day.day);
            const date = getDayDate(day.day, index);
            return (<div className={clas} key={day.day}>
                        <div className='day-name'>{name}</div>
                        <div className='day-date'>{date}</div>
                    </div>);
        });
        const icons = values.daily.data.map((day: any) => {
            const href = getIconHref(day.icon);
            return (<div className='week-column' key={day.day}><div className='day-icon'><img className="weather-icon" src={href} /></div></div>);
        });
        const tempBars = values.daily.data.map((day: any, index: number) => {
            if (index < tempBarHeights.length) {
                const topStyle = {height: tempBarHeights[index].top};
                const midStyle = {
                    height: tempBarHeights[index].mid, 
                    backgroundColor: tempBarHeights[index].color,
                    borderTop: '1px solid ' + tempBarHeights[index].borderTop,
                    borderBottom: '1px solid ' + tempBarHeights[index].borderBot,
                };
                const botStyle = {height: 10};
                return (
                    <div className='bar week-column' key={day.day}>
                        <div className='top' style={topStyle}>{tempBarHeights[index].maxTemp}</div>
                        <div className='mid' style={midStyle}></div>
                        <div className='bot' style={botStyle}>{tempBarHeights[index].minTemp}</div>
                    </div>
                );
            } else {
                return (<div className='bar week-column'></div>);
            }
        });
    
        const wind = values.daily.data.map((day: any) => {
            const value = Math.round(+day.all_day.wind.speed);
            const windDirStyle = {transform: `rotate(${day.all_day.wind.angle}deg)`};
            return (<div className='week-column day-wind' key={day.day}>{value}<i className='bi-arrow-up wind-icon' style={windDirStyle}></i></div>);
        });
        const maxPreci = tempBarHeights.map(x => x.precipitation).reduce(function(prev: number, curr: number) { return prev > curr ? prev : curr; });
        const precipitation = values.daily.data.map((day: any) => {
            const maxHeight = 20;
            const value = +day.all_day.precipitation.total;
            const color = value == 0 ? 'gray' : '#62b2ed'; 
            const height = maxPreci == 0 ? 0 : maxHeight * value / maxPreci;
            return (
                <div className='week-column day-preci' key={day.day}>
                    <div className='value' style={{color: color}}>{value}</div>
                    <div className='bar' style={{height: height}}></div>
                </div>
            );
        });
    
        return (
            <div className='widget-container'>
                <div className='widget-content' id='weather'>
                    <div className='week-row option-links'>
                        <span className='option-link'>Сейчас</span>
                        <span className='option-link'>Сегодня</span>
                        <span className='option-link'>Завтра</span>
                        <span className='option-link'>3 дня</span>
                        <span className='option-link active'>неделя</span>
                        <span className='option-link'>2 недели</span>
                    </div>
                    <div className='week-row widget-title'>
                        <span>Погода во Вроцлаве на 7 дней</span>
                    </div>
                    <div className='week-row days'>
                        {days}
                    </div>
                    <div className='week-row icons'>
                        {icons}
                    </div>
                    <div className='week-row subtitle'>
                        Температура воздуха, °C
                    </div>
                    <div className='week-row temperature'>
                        {tempBars}
                    </div>
                    <div className='week-row subtitle'>
                        Порывы ветра, м/c
                    </div>
                    <div className='week-row week-wind'>
                        {wind}
                    </div>
                    <div className='week-row subtitle'>
                        Осадки, мм
                    </div>
                    <div className='week-row week-precipitation'>
                        {precipitation}
                    </div>
                </div>
            </div>
        );
    } else {
        return <Spinner width={widgetWidth} height={widgetHeight} />;
    }
}

export default Weather;