import Dropdown from 'react-bootstrap/Dropdown';
import { getRemindLater, getRemindTomorrow, getRemindNextWeek } from './ItemTermin';
import { ITermin } from '../ItemTypes';


function ItemRemind({id, remind}: {id: number, remind: Date | null}) {

    function handleSelect(params: string | null) {
        console.log(params);
    }
    
    function delRemind() {
        console.log(`delTermin(${id})`);
    }
    
    let title = '';
    let titleClass = 'dates-title';
    if (!remind) {
        title = 'To remind';
    } else {
        const remindObj = new ITermin(remind.toString());
        let label = '';
        if (remindObj.is_expired) {
            label = 'Expired, ';
            titleClass += ' expired';
        } else {
            label = 'Termin: ';
            titleClass += ' actual';
        }
        title = label + remindObj.nice_date;

    }

    const remindLaterDT = getRemindLater(2);
    const remindLaterInfo = remindLaterDT.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    const remindTomorrowDT = getRemindTomorrow();
    const remindTomorrowInfo = new Intl.DateTimeFormat('en-GB', {
        weekday: 'short',
        hour: '2-digit',
        minute: '2-digit'
    }).format(remindTomorrowDT);
    const remindNextWeekDT = getRemindNextWeek(8);
    const remindNextWeekInfo = new Intl.DateTimeFormat('en-GB', {
        weekday: 'short',
        hour: '2-digit',
        minute: '2-digit'
    }).format(remindNextWeekDT);

    return (
        <div className="d-flex me-3 mb-2">
            <Dropdown onSelect={handleSelect}>
                <Dropdown.Toggle id="dropdown-remind" variant="light">
                    <i className="bi-check2-square" />
                    <div id="id_remind_title" className={titleClass}>
                        {title}
                    </div>
                </Dropdown.Toggle>

                <Dropdown.Menu className="super-colors">
                    <Dropdown.Item as="button" type="button" eventKey="later">
                        <div>
                            <i className="bi-clock"></i>
                            <span>Later</span>
                        </div>
                        <div className="info">{remindLaterInfo}</div>
                    </Dropdown.Item>
                    <Dropdown.Item as="button" type="button" eventKey="tomorrow">
                        <div>
                            <i className="bi-clock-history"></i>
                            <span>Tomorrow</span>
                        </div>
                        <div className="info">{remindTomorrowInfo}</div>
                    </Dropdown.Item>
                    <Dropdown.Item as="button" type="button" eventKey="nextWeek">
                        <div>
                            <i className="bi-calendar-week"></i>
                            <span>Next week</span>
                        </div>
                        <div className="info">{remindNextWeekInfo}</div>
                    </Dropdown.Item>
                    <Dropdown.Divider />
                    <Dropdown.Item as="button" type="button" eventKey="pickDateTime">
                        Pick a date and time
                    </Dropdown.Item>
                </Dropdown.Menu>
            </Dropdown>
            {remind && <>
                <button type="button" name="remind_delete" id="id_remind_delete" 
                    className="bi-x dates-del-icon" onClick={delRemind} />
            </>}
        </div>
    );
}

export default ItemRemind;