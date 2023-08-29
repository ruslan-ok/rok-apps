import { getIconHref } from './WeatherUtils';

export default function WeatherNow({values}: {values: any}) {
    const dt = new Date(values.current.event);
    const options = {
        weekday: "short",
        day: "numeric", 
        month: "long",
        year: "numeric",
        hour: "numeric",
        minute: "numeric",
    };
    // @ts-ignore
    const dateTime = dt.toLocaleDateString(undefined, options);
    const href = getIconHref(values.current.icon_num);
    const windValue = Math.round(+values.current.wind_speed);
    const windDirStyle = {transform: `rotate(${values.current.wind_angle}deg)`};
    const sign = values.current.temperature == 0 ? '' : values.current.temperature > 0 ? '+' : '-';
    const value = Math.abs(values.current.temperature);

    return (
        <div className='weather-now period-container'>
            <div className='week-row widget-title'>
                <span>Погода во Вроцлаве сейчас</span>
            </div>
            <div className='date-time'>{dateTime}</div>
            <div className='temp-and-icon'>
                <div className=''>
                    <img className="weather-now-icon" src={href} />
                </div>    
                <span className="unit unit_temperature_c">
                    <span className="sign">{sign}</span>{value}
                </span>
            </div>
            <div className='summary'>{values.current.summary}</div>
            <div className='kpi-list'>
                <div className='kpi wind'>
                    <div className='title'>Wind</div>
                    <div className='description'>
                        <div className='value'>
                            <div className='number'>{windValue}</div>
                            <div className='unit'>m/s</div>
                        </div>
                        <div className='info'><i className='bi-arrow-up wind-icon' style={windDirStyle}></i></div>
                    </div>
                </div>
                <div className='kpi clouds'>
                    <div className='title'>Clouds</div>
                    <div className='description'>
                        <div className='value'>
                            <div className='number'>{values.current.cloud_cover}</div>
                            <div className='unit'>%</div>
                        </div>
                        <div className='info'></div>
                    </div>
                </div>
                <div className={values.current.prec_type == 'none' ? 'd-none' : 'kpi precipitation'}>
                    <div className='title'>Precipitation</div>
                    <div className='description'>
                        <div className='value'>
                            <div className='number'>{values.current.prec_total}</div>
                            <div className='unit'>mm</div>
                        </div>
                        <div className='info'>{values.current.prec_type}</div>
                    </div>
                </div>
            </div>
        </div>
    );
}