import type { TempBarHeight } from './WeatherUtils';
import { getTempBarsInfo, getDayColor, getDayName, getDayDate, getIconHref } from './WeatherUtils';

export default function WeatherForTheWeek({values}: {values: any}) {

    const days = values.for_week.map((day: any, index: number) => {
        const color = getDayColor(day.event);
        const clas = 'week-column ' + color;
        const name = getDayName(day.event);
        const date = getDayDate(day.event, index);
        return (<div className={clas} key={day.event}>
                    <div className='day-name'>{name}</div>
                    <div className='day-date'>{date}</div>
                </div>);
    });

    const icons = values.for_week.map((day: any) => {
        const href = getIconHref(day.icon_num);
        return (<div className='week-column' key={day.event}><div className='day-icon'><img className="weather-icon" src={href} /></div></div>);
    });

    const tempBarHeights: TempBarHeight[] = getTempBarsInfo(values.for_week, true);
    const tempBars = values.for_week.map((day: any, index: number) => {
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
                <div className='bar week-column' key={day.event}>
                    <div className='top' style={topStyle}>{tempBarHeights[index].maxTemp}</div>
                    <div className='mid' style={midStyle}></div>
                    <div className='bot' style={botStyle}>{tempBarHeights[index].minTemp}</div>
                </div>
            );
        } else {
            return (<div className='bar week-column'></div>);
        }
    });

    const wind = values.for_week.map((day: any) => {
        const value = Math.round(+day.wind_speed);
        const windDirStyle = {transform: `rotate(${day.wind_angle}deg)`};
        return (<div className='week-column day-wind' key={day.event}>{value}<i className='bi-arrow-up wind-icon' style={windDirStyle}></i></div>);
    });

    const maxPreci = tempBarHeights.map(x => x.precipitation).reduce(function(prev: number, curr: number) { return prev > curr ? prev : curr; });
    const precipitation = values.for_week.map((day: any) => {
        const maxHeight = 20;
        const value = +day.prec_total;
        const color = value == 0 ? 'gray' : '#62b2ed'; 
        const height = maxPreci == 0 ? 0 : maxHeight * value / maxPreci;
        return (
            <div className='week-column day-preci' key={day.event}>
                <div className='value' style={{color: color}}>{value}</div>
                <div className='bar' style={{height: height}}></div>
            </div>
        );
    });


    return (
        <div className='weather-week period-container'>
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
    );
}