import type { TempBarHeight } from './WeatherUtils';
import { getTempBarsInfo, getDayColor, getDayName, getDayDate, getIconHref, checkWeekend, getWindColor } from './WeatherUtils';

export default function WeatherForTheWeek({values}: {values: any}) {

    const days = values.for_week.map((day: any, index: number) => {
        let cellClass: string[] = ['week-column'];
        checkWeekend(cellClass, day.event);
        cellClass.push(getDayColor(day.event));
        const name = getDayName(day.event);
        const date = getDayDate(day.event, index);
        return (<td className={cellClass.join(' ')} key={day.event}>
                    <div className='day-name'>{name}</div>
                    <div className='day-date'>{date}</div>
                </td>);
    });

    const icons = values.for_week.map((day: any) => {
        let cellClass: string[] = ['week-column'];
        checkWeekend(cellClass, day.event);
        const href = getIconHref(day.icon_num);
        return (
            <td className={cellClass.join(' ')} key={day.event}>
                <div className='day-icon'>
                    <img className="weather-icon" src={href} />
                </div>
            </td>
        );
    });

    function buildSubtitle(subtitle: string) {
        return values.for_week.map((day: any, index: number) => {
            let cellClass: string[] = ['week-column'];
            checkWeekend(cellClass, day.event);
            if (index == 0) {
                cellClass.push('overflow-td');
                return (
                    <td key={day.event} className={cellClass.join(' ')}>
                        <span className='subtitle-backgr'>{subtitle}</span>
                    </td>
                );
            }
            return (<td key={day.event} className={cellClass.join(' ')}></td>);
        });
    }

    const titleTemp = buildSubtitle('Температура воздуха, °C');

    const tempBarHeights: TempBarHeight[] = getTempBarsInfo(values.for_week, true);
    const tempBars = values.for_week.map((day: any, index: number) => {
        let cellClass: string[] = ['week-column bar'];
        checkWeekend(cellClass, day.event);
        if (index >= tempBarHeights.length) {
            return (<div className={cellClass.join(' ')}></div>);
        } else {
            const topStyle = {height: tempBarHeights[index].top};
            const midStyle = {
                height: tempBarHeights[index].mid, 
                backgroundColor: tempBarHeights[index].color,
                borderTop: '1px solid ' + tempBarHeights[index].borderTop,
                borderBottom: '1px solid ' + tempBarHeights[index].borderBot,
            };
            const botStyle = {height: 10};
            return (
                <td className={cellClass.join(' ')} key={day.event}>
                    <div className='top' style={topStyle}>{tempBarHeights[index].maxTemp}</div>
                    <div className='mid' style={midStyle}></div>
                    <div className='bot' style={botStyle}>{tempBarHeights[index].minTemp}</div>
                </td>
            );
        }
    });

    const titleWind = buildSubtitle('Порывы ветра, м/c');
    
    const wind = values.for_week.map((day: any) => {
        let cellClass: string[] = ['week-column day-wind'];
        checkWeekend(cellClass, day.event);
        const value = Math.round(+day.wind_speed);
        const windDirStyle = {transform: `rotate(${day.wind_angle}deg)`};
        const windValueStyle = {color: getWindColor(value)};
        return (
            <td className={cellClass.join(' ')} key={day.event} style={windValueStyle}>
                {value}
                <i className='bi-arrow-up wind-icon' style={windDirStyle}></i>
            </td>
        );
    });

    const titlePreci = buildSubtitle('Осадки, мм');
    
    const maxPreci = tempBarHeights.map(x => x.precipitation).reduce(function(prev: number, curr: number) { return prev > curr ? prev : curr; });
    const precipitation = values.for_week.map((day: any) => {
        let cellClass: string[] = ['week-column day-preci'];
        checkWeekend(cellClass, day.event);
        const maxHeight = 20;
        const value = +day.prec_total;
        const color = value == 0 ? 'gray' : 'var(--rain-color)'; 
        const height = maxPreci == 0 ? 0 : maxHeight * value / maxPreci;
        return (
            <td className={cellClass.join(' ')} key={day.event}>
                <div className='value' style={{color: color}}>{value}</div>
                <div className='bar' style={{height: height}}></div>
            </td>
        );
    });


    return (
        <div className='weather-week period-container'>
            <div className='week-row widget-title'>
                <span className='location'>{values.place}</span><span className='period'>: погода на неделю</span>
            </div>
            <table className="table table-borderles">
                <tbody>
                    <tr className='week-row days'>
                        {days}
                    </tr>
                    <tr className='week-row icons'>
                        {icons}
                    </tr>
                    <tr className='week-row subtitle'>
                        {titleTemp}
                    </tr>
                    <tr className='week-row temperature'>
                        {tempBars}
                    </tr>
                    <tr className='week-row subtitle'>
                       {titleWind}
                    </tr>
                    <tr className='week-row week-wind'>
                        {wind}
                    </tr>
                    <tr className='week-row subtitle'>
                        {titlePreci}
                    </tr>
                    <tr className='week-row week-precipitation'>
                        {precipitation}
                    </tr>
                </tbody>
            </table>
        </div>
    );
}