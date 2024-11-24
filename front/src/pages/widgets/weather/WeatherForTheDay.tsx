import type { ITempBarHeight } from './WeatherUtils';
import { getDayName, getDayDate, getDayColor, getIconHref, getHourNum, getTempBarsInfo, checkNight, getWindColor } from './WeatherUtils';

export default function WeatherForTheDay({values}: {values: any}) {

    let d1_day: number | undefined;
    let d2_day: number | undefined;
    let d1_day_str: string;
    let d2_day_str: string;
    let d1_span = 0;
    let d1_span_correct = 0;
    let d2_span_correct = 0;
    for (let i = 0; i < values.for_day.length; i++) {
        const dt = new Date(values.for_day[i].event);
        if (i === 0) {
            d1_day = dt.getDate();
            d1_day_str = dt.toString();
        }
        else {
            if (d2_day === undefined && d1_day !== dt.getDate()) {
                d2_day = dt.getDate();
                d2_day_str = dt.toString();
            }
        }
        if (d2_day === undefined)
            d1_span++;
    }

    if (d1_span % 3 === 1) {
        d1_span_correct--;
        d2_span_correct++;
    }
    if (d1_span % 3 === 2) {
        d1_span_correct++;
        d2_span_correct--;
    }

    let aggs = [];
    let curr = [];
    for (let i = 0; i < values.for_day.length; i++) {
        curr.push(i);
        if (curr.length === 3 || (aggs.length === 0 && curr.length === 2 && d1_span_correct === 1)) {
            aggs.push(curr);
            curr = [];
        }
        if (i === 0 && d2_span_correct === 1)
            curr = [];
    }
    if (curr.length > 1)
        aggs.push(curr);

    const sunrise_dt = new Date(values.sunrise);
    const sunset_dt = new Date(values.sunset);
    const sunrise = sunrise_dt.getHours();
    const sunset = sunset_dt.getHours();

    const days = values.for_day.map((hour: any, index: number) => {
        let cellClass: string[] = [];
        checkNight(cellClass, hour.event, d1_span_correct, sunrise, sunset);

        let name = '';
        if (index === 0) {
            name = getDayName(d1_day_str) + ' ' + getDayDate(hour.event, 0);
            cellClass.push('day-name overflow-td ' + getDayColor(hour.event));
        }
        else {
            if (d2_day !== undefined && index === (d1_span + d1_span_correct)) {
                name = getDayName(d2_day_str) + ' ' + getDayDate(hour.event, 0);
                cellClass.push('day-name overflow-td ' + getDayColor(hour.event));
            }
        }
        return (<td key={hour.event} className={cellClass.join(' ')}>{name}</td>);
    });
    
    const hours = values.for_day.map((hour: any, index: number) => {
        let cellClass: string[] = ['hour-name'];
        checkNight(cellClass, hour.event, d1_span_correct, sunrise, sunset);
        const hourNum = getHourNum(hour.event, d1_span_correct);
        let name = '', sup;
        if (index % 3 === 0) {
            name = hourNum.toString();
            sup = <sup className="time-sup">00</sup>;
        }
        return (<td key={hour.event} className={cellClass.join(' ')}>
            {name}{sup}
        </td>);
    });
    
    const icons = values.for_day.map((hour: any, index: number) => {
        let cellClass: string[] = [];
        checkNight(cellClass, hour.event, d1_span_correct, sunrise, sunset);
        if (index % 3 !== 1) {
            return (<td key={hour.event} className={cellClass.join(' ')}></td>);
        }
        cellClass.push('icon-td');
        const href = getIconHref(values.for_day[index - d1_span_correct].icon_num);
        return (
            <td key={hour.event} className={cellClass.join(' ')}>
                <div className='hours-icon'><img className="weather-icon" src={href} alt="Weather icon"/></div>
            </td>
        );
    });

    function buildSubtitle(subtitle: string) {
        return values.for_day.map((hour: any, index: number) => {
            let cellClass: string[] = [];
            checkNight(cellClass, hour.event, d1_span_correct, sunrise, sunset);
            if (index === 0) {
                cellClass.push('overflow-td');
                return (
                    <td key={hour.event} className={cellClass.join(' ')}>
                        <span className='subtitle-backgr'>{subtitle}</span>
                    </td>
                );
            }
            return (<td key={hour.event} className={cellClass.join(' ')}></td>);
        });
    }

    const titleTemp = buildSubtitle('Температура воздуха, °C');
    
    const tempBarHeights: ITempBarHeight[] = getTempBarsInfo(values.for_day, false);
    const tempBars = values.for_day.map((hour: any, index: number) => {
        let cellClass: string[] = ['bar day-column'];
        checkNight(cellClass, hour.event, d1_span_correct, sunrise, sunset);
        if (index < tempBarHeights.length) {
            const topStyle = {height: tempBarHeights[index].top};
            const midStyle = {
                height: 15, 
                backgroundColor: tempBarHeights[index].color,
                borderTop: '1px solid ' + tempBarHeights[index].borderTop,
                borderBottom: '1px solid ' + tempBarHeights[index].borderBot,
            };
            const botStyle = {height: 25};
            return (
                <td className={cellClass.join(' ')} key={hour.event}>
                    <div className='top' style={topStyle}></div>
                    <div className='mid' style={midStyle}></div>
                    <div className='bot overflow-td' style={botStyle}>{index % 3 === 1 ? tempBarHeights[index].avgTemp : ''}</div>
                </td>
            );
        } else {
            return (<div className={cellClass.join(' ')}></div>);
        }
    });

    const titleWind = buildSubtitle('Порывы ветра, м/c');
    
    const wind = values.for_day.map((hour: any) => {
        let cellClass: string[] = ['day-column hour-wind'];
        checkNight(cellClass, hour.event, d1_span_correct, sunrise, sunset);
        const value = Math.round(+hour.wind_speed);
        const windDirStyle = {transform: `rotate(${hour.wind_angle}deg)`};
        const windValueStyle = {color: getWindColor(value)};
        return (
            <td className={cellClass.join(' ')} key={hour.event} style={windValueStyle}>
                {value}
                <i className='bi-arrow-up wind-icon' style={windDirStyle}></i>
            </td>
        );
    });

    const titlePreci = buildSubtitle('Осадки, мм');
    
    const maxPreci = tempBarHeights.map(x => +x.precipitation).reduce(function(prev: number, curr: number) { return prev > curr ? prev : curr; });
    const precipitation = values.for_day.map((hour: any) => {
        let cellClass: string[] = ['day-column hour-perci-td'];
        checkNight(cellClass, hour.event, d1_span_correct, sunrise, sunset);
        const maxHeight = 20;
        const value = +hour.prec_total;
        const color = value === 0 ? 'gray' : '#62b2ed'; 
        const height = maxPreci === 0 ? 0 : maxHeight * value / maxPreci;
        return (
            <td className={cellClass.join(' ')} key={hour.event}>
                <div className='hour-preci'>
                    <div className='value' style={{color: color}}>{value}</div>
                    <div className='bar' style={{height: height}}></div>
                </div>
            </td>
        );
    });


    return (
        <div className='weather-day period-container'>
            <div className='week-row widget-title'>
                <span className='location'>{values.place}</span><span className='period'>: погода на сутки</span>
            </div>
            <table className="table table-borderles">
            {/* <>table-bordered</>
            <>table-borderles</> */}
                <tbody>
                    <tr>
                        {days}
                    </tr>
                    <tr>
                        {hours}
                    </tr>
                    <tr>
                        {icons}
                    </tr>
                    <tr>
                        {titleTemp}
                    </tr>
                    <tr>
                        {tempBars}
                    </tr>
                    <tr>
                       {titleWind}
                    </tr>
                    <tr>
                        {wind}
                    </tr>
                    <tr>
                        {titlePreci}
                    </tr>
                    <tr>
                        {precipitation}
                    </tr>
                </tbody>
            </table>
        </div>
    );
}