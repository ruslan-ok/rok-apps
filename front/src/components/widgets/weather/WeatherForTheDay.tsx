import type { TempBarHeight } from './WeatherUtils';
import { getDayDate, getIconHref, getHourNum, getHourName, getTempBarsInfo } from './WeatherUtils';

export default function WeatherForTheDay({values}: {values: any}) {

    let d1_day;
    let d2_day;
    let d1_span = 0;
    let d2_span = 0;
    let d1_span_correct = 0;
    let d2_span_correct = 0;
    let days;
    for (let i = 0; i < values.for_day.length; i++) {
        const dt = new Date(values.for_day[i].event);
        if (i == 0)
            d1_day = dt.getDate();
        else 
            if (d2_day == undefined && d1_day != dt.getDate())
                d2_day = dt.getDate();

        if (d2_day == undefined)
            d1_span++;
        else
            d2_span++;
    }

    if (d1_span % 3 == 1) {
        d1_span_correct--;
        d2_span_correct++;
    }
    if (d1_span % 3 == 2) {
        d1_span_correct++;
        d2_span_correct--;
    }

    let aggs = [];
    let curr = [];
    for (let i = 0; i < values.for_day.length; i++) {
        curr.push(i);
        if (curr.length == 3 || (aggs.length == 0 && curr.length == 2 && d1_span_correct == 1)) {
            aggs.push(curr);
            curr = [];
        }
        if (i == 0 && d2_span_correct == 1)
            curr = [];
    }
    if (curr.length > 1)
        aggs.push(curr);

    if (d2_day == undefined || d2_span == 0)
        days = (
            <td key={d1_day} colSpan={d1_span}>
                {getDayDate(values.for_day[0].event, 0)}
            </td>);
    else
        days = ([
            <td key={d1_day} colSpan={d1_span + d1_span_correct}>
                {getDayDate(values.for_day[0].event, 0)}
            </td>,
            <td key={d2_day} colSpan={d2_span + d2_span_correct}>
                {getDayDate(values.for_day[d1_span].event, 1)}
            </td>
        ]);

    const hours = aggs.map((group: number[]) => {
        const name = getHourName(values.for_day[group[0]].event);
        return (<td key={group[0]} colSpan={3} className='hour-name'>
            {name}<sup className="time-sup">00</sup>
        </td>);
    });
    
    const icons = aggs.map((group: number[]) => {
    const href = getIconHref(values.for_day[group[1]].icon_num);
        return (
            <td key={group[0]} colSpan={3}>
                <div className='hours-icon'><img className="weather-icon" src={href} /></div>
            </td>
        );
    });

    const tempBarHeights: TempBarHeight[] = getTempBarsInfo(values.for_day, false);
    const tempBars = values.for_day.map((day: any, index: number) => {
        if (index < tempBarHeights.length) {
            const hour = getHourNum(day.event) + d2_span_correct;
            const night = (hour > 19 || hour < 7);
            const topStyle = {height: tempBarHeights[index].top};
            const midStyle = {
                height: 15, 
                backgroundColor: tempBarHeights[index].color,
                borderTop: '1px solid ' + tempBarHeights[index].borderTop,
                borderBottom: '1px solid ' + tempBarHeights[index].borderBot,
            };
            const botStyle = {height: 25};
            return (
                <td className={night ? 'bar day-column night' :  'bar day-column'} key={day.event}>
                    <div className='top' style={topStyle}></div>
                    <div className='mid' style={midStyle}></div>
                    <div className='bot' style={botStyle}>{index % 3 == 1 ? tempBarHeights[index].avgTemp : ''}</div>
                </td>
            );
        } else {
            return (<div className='bar day-column'></div>);
        }
    });

    const wind = values.for_day.map((day: any) => {
        const value = Math.round(+day.wind_speed);
        const windDirStyle = {transform: `rotate(${day.wind_angle}deg)`};
        return (<td className='day-column hour-wind' key={day.event}>{value}<i className='bi-arrow-up wind-icon' style={windDirStyle}></i></td>);
    });

    const maxPreci = tempBarHeights.map(x => x.precipitation).reduce(function(prev: number, curr: number) { return prev > curr ? prev : curr; });
    const precipitation = values.for_day.map((hour: any) => {
        const maxHeight = 20;
        const value = +hour.prec_total;
        const color = value == 0 ? 'gray' : '#62b2ed'; 
        const height = maxPreci == 0 ? 0 : maxHeight * value / maxPreci;
        return (
            <td className='day-column hour-perci-td' key={hour.event}>
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
                <span>Погода во Вроцлаве на сутки</span>
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
                        <td colSpan={values.for_day.length}>
                            Температура воздуха, °C
                        </td>
                    </tr>
                    <tr>
                        {tempBars}
                    </tr>
                    <tr>
                        <td colSpan={values.for_day.length}>
                            Порывы ветра, м/c
                        </td>
                    </tr>
                    <tr>
                        {wind}
                    </tr>
                    <tr>
                        <td colSpan={values.for_day.length}>
                            Осадки, мм
                        </td>
                    </tr>
                    <tr>
                        {precipitation}
                    </tr>
                </tbody>
            </table>
        </div>
    );
}