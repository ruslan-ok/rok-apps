import { useState, SyntheticEvent } from 'react';
import Form from 'react-bootstrap/Form';
import Dropdown from 'react-bootstrap/Dropdown';
import { extraClass } from '../../PageConfig';
import { ITermin } from '../ItemTypes';


export function getRemindLater(hours: number) {
    let remindLater = new Date();
    
    // Add specified hours to the current time
    remindLater.setHours(remindLater.getHours() + hours);

    // Adjust minutes if they're greater than zero
    if (remindLater.getMinutes() > 0) {
        let correctMin;
        if (remindLater.getMinutes() > 30) {
            correctMin = 60 - remindLater.getMinutes();
        } else {
            correctMin = -remindLater.getMinutes();
        }
        remindLater.setMinutes(remindLater.getMinutes() + correctMin);
    }
    remindLater.setSeconds(0);
    remindLater.setMilliseconds(0);

    return remindLater;
}

export function getRemindTomorrow() {
    const reminderDate = new Date();
    
    // Set reminder time to 9:00 AM tomorrow
    reminderDate.setDate(reminderDate.getDate() + 1);
    reminderDate.setHours(9, 0, 0, 0);
    
    return reminderDate;
}

export function getRemindNextWeek(days: number) {
    const now = new Date();
    const currentDayOfWeek = now.getDay() || 7; // Adjust for Sunday as 7
    const reminderDate = new Date(now);

    // Set reminder time to 9:00 AM
    reminderDate.setHours(9, 0, 0, 0);

    // Calculate days until the specified weekday next week
    const daysUntilNextReminder = days - currentDayOfWeek + 7;
    reminderDate.setDate(now.getDate() + daysUntilNextReminder);

    return reminderDate;
}

function toJSONLocal(value: string): string {
    function addZ(n: number): string {
      return (n < 10? '0' : '') + n;
    }
    const dt = new Date(value);
    return dt.getFullYear() + '-' + 
           addZ(dt.getMonth() + 1) + '-' + 
           addZ(dt.getDate()) + 'T' +
           addZ(dt.getHours()) + ':' +
           addZ(dt.getMinutes());
} 

function ItemTermin({termin, onChange}: {termin: string, onChange: Function}) {
    const [picker, setPicker] = useState(false);
    const [value, setValue] = useState(termin);

    const terminLaterDT = getRemindLater(3);
    const terminTomorrowDT = getRemindTomorrow();
    const terminNextWeekDT = getRemindNextWeek(8);

    function handleSelect(params: string | null) {
        switch (params) {
            case 'later': {
                const newValue = terminLaterDT.toJSON();
                setValue(newValue);
                onChange({set_stop: newValue});
                break;
            }
            case 'tomorrow': {
                const newValue = terminTomorrowDT.toJSON();
                setValue(newValue);
                onChange({set_stop: newValue});
                break;
            }
            case 'nextWeek': {
                const newValue = terminNextWeekDT.toJSON();
                setValue(newValue);
                onChange({set_stop: newValue});
                break;
            }
            case 'pickDateTime': {
                setPicker(true);
                break;
            }
        }
    }
    
    function delTermin() {
        setValue('');
        onChange({set_stop: null});
    }

    function datePicked(event: SyntheticEvent) {
        const value = event.target.value;
        setValue(value);
        onChange({stop: value});
    }

    function hideTermin() {
        setPicker(false);
    }
    
    let title = '';
    let titleClass = 'dates-title';
    if (!value) {
        title = 'Add due date';
    } else {
        const terminObj = new ITermin(value);
        let label = '';
        if (terminObj.is_expired) {
            label = 'Expired, ';
            titleClass += ' expired';
        } else {
            label = 'Termin: ';
            titleClass += ' actual';
        }
        title = label + terminObj.nice_date;
    }

    const terminLaterInfo = terminLaterDT.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    const terminTomorrowInfo = new Intl.DateTimeFormat('en-GB', {
        weekday: 'short',
        hour: '2-digit',
        minute: '2-digit'
    }).format(terminTomorrowDT);
    const terminNextWeekInfo = new Intl.DateTimeFormat('en-GB', {
        weekday: 'short',
        hour: '2-digit',
        minute: '2-digit'
    }).format(terminNextWeekDT);

    const localValue = toJSONLocal(value);

    return (
        <div className="d-flex flex-column me-3 mb-2">
            <div className="d-flex">
                <Dropdown onSelect={handleSelect}>
                    <Dropdown.Toggle id="dropdown-termin" variant="light">
                        <i className="bi-check2-square" />
                        <div id="id_termin_title" className={titleClass}>
                            {title}
                        </div>
                    </Dropdown.Toggle>

                    <Dropdown.Menu className="super-colors">
                        <Dropdown.Item as="button" type="button" eventKey="later">
                            <div>
                                <i className="bi-calendar4"></i>
                                <span>Later</span>
                            </div>
                            <div className="info">{terminLaterInfo}</div>
                        </Dropdown.Item>
                        <Dropdown.Item as="button" type="button" eventKey="tomorrow">
                            <div>
                                <i className="bi-calendar4-event"></i>
                                <span>Tomorrow</span>
                            </div>
                            <div className="info">{terminTomorrowInfo}</div>
                        </Dropdown.Item>
                        <Dropdown.Item as="button" type="button" eventKey="nextWeek">
                            <div>
                                <i className="bi-calendar4-week"></i>
                                <span>Next week</span>
                            </div>
                            <div className="info">{terminNextWeekInfo}</div>
                        </Dropdown.Item>
                        <Dropdown.Divider />
                        <Dropdown.Item as="button" type="button" eventKey="pickDateTime">
                            <div>
                                <i className="bi-calendar2-date"></i>
                                <span>Pick date and time</span>
                            </div>
                        </Dropdown.Item>
                    </Dropdown.Menu>
                </Dropdown>
                {value && <>
                    <button type="button" name="termin_delete" id="id_termin_delete" 
                        className="bi-x dates-del-icon" onClick={delTermin} />
                </>}
            </div>
            <div className={extraClass('d-flex', !picker, 'd-none')}>
                <Form.Control type={picker ? "datetime-local" : "hidden"} name="stop" defaultValue={localValue} onChange={datePicked}/>
                <button type="button" name="termin_hide" id="id_termin_hide" 
                        className="bi-chevron-up dates-del-icon" onClick={hideTermin} />
            </div>
        </div>
    );
}

export default ItemTermin;