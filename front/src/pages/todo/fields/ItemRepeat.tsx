// import { useState } from 'react';
import Dropdown from 'react-bootstrap/Dropdown';


const NONE = 0;
const DAILY = 1;
const WORKDAYS = 2;
const WEEKLY = 3;
const MONTHLY = 4;
const YEARLY = 5;

const MON = 1;
const TUE = 2;
const WEN = 4;
const THR = 8;
const FRI = 16;
const WORK_DAYS = MON + TUE + WEN + THR + FRI;

const REPEAT = [
    [NONE, 'No'],
    [DAILY, 'Daily'],
    [WORKDAYS, 'Workdays'],
    [WEEKLY, 'Weekly'],
    [MONTHLY, 'Monthly'],
    [YEARLY, 'Yearly']
];

const REPEAT_NAME = {
    [DAILY]: 'days',
    [WEEKLY]: 'weeks',
    [MONTHLY]: 'months',
    [YEARLY]: 'years'
};

function s_repeat(repeat: number, repeat_num: number): string {
    if (!repeat || repeat === NONE) return '';

    if (repeat_num === 1) {
        return repeat === WORKDAYS 
            ? '' + REPEAT[WEEKLY][1]
            : '' + REPEAT[repeat][1];
    }

    const repeatName = repeat ? REPEAT_NAME[repeat]: '';
    return `Once every ${repeat_num} ${repeatName}`;
}

function weekDayName(date: Date) {
    const options: Intl.DateTimeFormatOptions = { weekday: 'short' };
    return new Intl.DateTimeFormat('en-GB', options).format(date);
}

function repeat_s_days(repeat: number, repeat_days: number, start: string, stop: string): string {
    if (repeat === WEEKLY) {
        if (repeat_days === 0) {
            const dStart = start ? new Date(start) : null;
            const dStop = stop ? new Date(stop) : null;
            const ddd = dStop || dStart;
            if (ddd) {
                return weekDayName(ddd);
            }
            return '???';
        }

        if (repeat_days === WORK_DAYS) {
            return 'Workdays';
        }

        let ret = '';
        const monday = new Date(2020, 6, 6); // July 6, 2020 is a Monday

        for (let i = 0; i < 7; i++) {
            if (repeat_days || 0 & (1 << i)) {
                if (ret) ret += ', ';
                ret += weekDayName(new Date(monday.getTime() + i * 86400000));
            }
        }
        return ret;
    }
    return '';
}

function ItemRepeat({repeat, days, num, start, stop, onChange}: {repeat: number | null, days: number | null, num: number | null, start: string, stop: string, onChange: Function}) {
    // const [picker, setPicker] = useState(false);
    // const [state, setState] = useState({mode: repeat, num: num, days: days});

    function handleSelect(params: string | null) {
        console.log(params);
        switch (params) {
            case 'day': {
                // setState({mode: DAILY, num: 1, days: null});
                onChange({set_repeat: DAILY, set_repeat_num: 1, set_repeat_days: null});
                break;
            }
            case 'work': {
                // setState({mode: WEEKLY, num: 1, days: WORK_DAYS});
                onChange({set_repeat: WEEKLY, set_repeat_num: 1, set_repeat_days: WORK_DAYS});
                break;
            }
            case 'week': {
                // setState({mode: WEEKLY, num: 1, days: null});
                onChange({set_repeat: WEEKLY, set_repeat_num: 1, set_repeat_days: null});
                break;
            }
            case 'month': {
                // setState({mode: MONTHLY, num: 1, days: null});
                onChange({set_repeat: MONTHLY, set_repeat_num: 1, set_repeat_days: null});
                break;
            }
            case 'year': {
                // setState({mode: YEARLY, num: 1, days: null});
                onChange({set_repeat: YEARLY, set_repeat_num: 1, set_repeat_days: null});
                break;
            }
            case 'custom': {
                setPicker(true);
                break;
            }
        }
    }

    function delRepeat() {
        console.log(`delRepeat`);
        // setState({mode: null, num: null, days: null});
        onChange({set_repeat: null, set_repeat_num: null, set_repeat_days: null});
    }

    let title = <></>;
    let titleClass = 'dates-title';
    if (!repeat) {
        title = <>Repeat</>;
    } else {
        const sRepeat = s_repeat(repeat, num);
        const sDays = repeat_s_days(repeat, days, start, stop);
        title = <>
            <div className='actual'>{sRepeat}</div>
            <div className="description">{sDays}</div>
        </>;
    }

    return (
        <div className="d-flex flex-column me-3 mb-2">
            <div className="d-flex">
                <Dropdown onSelect={handleSelect}>
                    <Dropdown.Toggle id="dropdown-repeat" variant="light">
                        <i className="bi-arrow-repeat" />
                        <div id="id_repeat_title" className={titleClass}>
                            {title}
                        </div>
                    </Dropdown.Toggle>

                    <Dropdown.Menu className="super-colors">
                    <Dropdown.Item as="button" type="button" eventKey="day">
                            <div>
                                <i className="bi-calendar2-date"></i>
                                <span>Daily</span>
                            </div>
                        </Dropdown.Item>
                        <Dropdown.Item as="button" type="button" eventKey="work">
                            <div>
                                <i className="bi-calendar2-week"></i>
                                <span>Workdays</span>
                            </div>
                        </Dropdown.Item>
                        <Dropdown.Item as="button" type="button" eventKey="week">
                            <div>
                                <i className="bi-calendar2-week"></i>
                                <span>Weekly</span>
                            </div>
                        </Dropdown.Item>
                        <Dropdown.Item as="button" type="button" eventKey="month">
                            <div>
                                <i className="bi-calendar2-month"></i>
                                <span>Monthly</span>
                            </div>
                        </Dropdown.Item>
                        <Dropdown.Item as="button" type="button" eventKey="year">
                            <div>
                                <i className="bi-calendar2-range"></i>
                                <span>Yearly</span>
                            </div>
                        </Dropdown.Item>
                        <Dropdown.Divider />
                        <Dropdown.Item as="button" type="button" eventKey="custom">
                            Custom
                        </Dropdown.Item>
                    </Dropdown.Menu>
                </Dropdown>
                {repeat !== 0 && <>
                    <button type="button" name="termin_delete" id="id_termin_delete" 
                        className="bi-x dates-del-icon" onClick={delRepeat} />
                </>}
            </div>
            {/* {picker && <div className="d-flex">
                <Form.Control type="datetime-local" name="stop" defaultValue={localValue} onChange={datePicked}/>
                <button type="button" name="termin_hide" id="id_termin_hide" 
                        className="bi-chevron-up dates-del-icon" onClick={hideTermin} />
            </div>} */}
        </div>
    );
}

export default ItemRepeat;