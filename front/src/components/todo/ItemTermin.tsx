import { IItemInfo } from './ItemTypes';
import { extraClass } from './TodoItemPage';

function toggleSelectField() {
    console.log('toggleSelectField');
}

function delTermin() {
    console.log('delTermin');
}

function terminToday() {
    console.log('terminToday');
}

function terminTomorrow() {
    console.log('terminTomorrow');
}

function terminNextWeek() {
    console.log('terminNextWeek');
}

function delRepeat() {
    console.log('delRepeat');
}

function repeatSet() {
    const num: number = 5;
    console.log(`repeatSet(${num})`);
}

function dayClick() {
    const num: number = 5;
    console.log(`dayClick(${num})`);
}

function delRemind() {
    console.log('delRemind');
}

function remindToday() {
    console.log('remindToday');
}

function remindTomorrow() {
    console.log('remindTomorrow');
}

function remindNextWeek() {
    console.log('remindNextWeek');
}


function getRemindLater(hours: number) {
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

    return remindLater;
}

function getRemindTomorrow() {
    const reminderDate = new Date();
    
    // Set reminder time to 9:00 AM tomorrow
    reminderDate.setDate(reminderDate.getDate() + 1);
    reminderDate.setHours(9, 0, 0, 0);
    
    return reminderDate;
}

function getRemindNextWeek(days: number) {
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

function ItemTermin({item}: {item: IItemInfo}) {
    const terminInfo = item.stop ? item.termin_info : '';
    const addDueDate = item.stop ? '' : 'Add due date';

    const terminLaterDT = getRemindLater(3);
    const terminLaterInfo = terminLaterDT.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
    const terminTomorrowDT = getRemindTomorrow();
    const terminTomorrowInfo = new Intl.DateTimeFormat('en-GB', {
        weekday: 'short',
        hour: '2-digit',
        minute: '2-digit'
    }).format(terminTomorrowDT);
    const terminNextWeekDT = getRemindNextWeek(8);
    const terminNextWeekInfo = new Intl.DateTimeFormat('en-GB', {
        weekday: 'short',
        hour: '2-digit',
        minute: '2-digit'
    }).format(terminNextWeekDT);
    const repeat_form_d1 = item.getWeekDayName(1);
    const repeat_form_d2 = item.getWeekDayName(2);
    const repeat_form_d3 = item.getWeekDayName(3);
    const repeat_form_d4 = item.getWeekDayName(4);
    const repeat_form_d5 = item.getWeekDayName(5);
    const repeat_form_d6 = item.getWeekDayName(6);
    const repeat_form_d7 = item.getWeekDayName(7);

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

    return (<>
        <div className="termin-block-expandable">
            {/* <!-- Task.stop VIEW -->
            {{ form.stop.errors }}  */}
            <div className="termin-block" id="termin-view">
                <button className="termin-block__content" onClick={toggleSelectField}>
                    <i className="bi-check2-square termin-block__icon" />
                    <div id="id_termin_title" className={extraClass(extraClass('termin-block__title', item.is_expired, 'expired'), item.is_actual, 'actual')}>
                        {terminInfo}
                        {addDueDate}
                    </div>
                </button>
                {item.stop &&
                    <button name="termin_delete" id="id_termin_delete" className="bi-x del-item-icon" onClick={delTermin} />
                }
            </div>

            {/* <!-- Task.stop SELECT --> */}
            <div className="section-item d-none" id="termin-select">
                <div className="dropdown-content-separator" />
                <button className="dropdown-content-item c001" name="termin_today" onClick={terminToday}>
                    <div className="c002">
                        <i className="bi-calendar4"></i>
                        <span className="c003">Later</span>
                    </div>
                    <div className="c004">{terminLaterInfo}</div>
                </button>
                <button className="dropdown-content-item c001" name="termin_tomorrow" onClick={terminTomorrow}>
                    <div className="c002">
                        <i className="bi-calendar4-event"></i>
                        <span className="c003">Tomorrow</span>
                    </div>
                    <div className="c004">{terminTomorrowInfo}</div>
                </button>
                <button className="dropdown-content-item c001" name="termin_next_week" onClick={terminNextWeek}>
                    <div className="c002">
                        <i className="bi-calendar4-week"></i>
                        <span className="c003">Next week</span>
                    </div>
                    <div className="c004">{terminNextWeekInfo}</div>
                </button>
                <div className="section-inner">
                    <div className="section-content">
                        <div className="section-title" />
                        {item.stop}
                    </div>
                </div>
                <div className="dropdown-content-separator" />
            </div>

        </div>
            
        <div className="termin-block-expandable">
            {/* {{ form.repeat_num.errors }}
            {{ form.repeat.errors }}
            {{ form.repeat_days.errors }} */}
            {/* <!-- Task.repeat VIEW --> */}
            <div className="termin-block" id="repeat-view">
                <button className="termin-block__content" onClick={toggleSelectField} >
                    <i className="bi-arrow-repeat termin-block__icon"></i>
                    <div id="id_repeat_title" className="termin-block__title">
                        {item.repeat && item.repeat !== 0 ?
                            <>
                                <div className={extraClass('', item.repeat !== 0, 'actual')}>{item.s_repeat}</div>
                                <div className="termin-block__description">{item.repeat_s_days}</div>
                            </>
                            : 
                            <span>Repeat</span>
                        }
                    </div>
                </button>
                {item.repeat &&
                    <button name="repeat_delete" id="id_repeat_delete" className="bi-x del-item-icon" onClick={delRepeat} />
                }
            </div>

            {/* <!-- Task.repeat SELECT --> */}
            <div className="section-item d-none" id="repeat-select">
                <div className="dropdown-content-separator"></div>
                <button className="dropdown-content-item c001" name="repeat_daily" onClick={repeatSet} >
                    <div className="c002">
                        <i className="bi-calendar2-date" />
                        <span className="c003">Daily</span>
                    </div>
                </button>
                <button className="dropdown-content-item c001" name="repeat_workdays" onClick={repeatSet} >
                    <div className="c002">
                        <i className="bi-calendar2-day" />
                        <span className="c003">Work days</span>
                    </div>
                </button>
                <button className="dropdown-content-item c001" name="repeat_weekly" onClick={repeatSet} >
                    <div className="c002">
                        <i className="bi-calendar2-week" />
                        <span className="c003">Weekly</span>
                    </div>
                </button>
                <button className="dropdown-content-item c001" name="repeat_monthly" onClick={repeatSet} >
                    <div className="c002">
                        <i className="bi-calendar2-month" />
                        <span className="c003">Monthly</span>
                    </div>
                </button>
                <button className="dropdown-content-item c001" name="repeat_annually" onClick={repeatSet} >
                    <div className="c002">
                        <i className="bi-calendar2-range" />
                        <span className="c003">Annually</span>
                    </div>
                </button>
                <div className="dropdown-content-separator" />
                <div className="dropdown-content-title-part">Repeat every...</div>
                <div className="repeat-options-block">
                    <div className="repeat-options-main">
                        <i className="bi-calendar2" />
                        <div className="repeat-options-input">
                            <div className="repeat-options-num">{item.repeat_num}</div>
                            <div className="repeat-options-type">{item.repeat}</div>
                        </div>
                        <div>&nbsp;</div>
                    </div>
                    <div className="repeat-options-week">
                        <input type="hidden" id="id_repeat_days" name="repeat_days" value="{{ form.repeat_days.value }}" />
                        <button id="d1" className="button day" onClick={dayClick} >{repeat_form_d1}</button>
                        <button id="d2" className="button day" onClick={dayClick} >{repeat_form_d2}</button>
                        <button id="d3" className="button day" onClick={dayClick} >{repeat_form_d3}</button>
                        <button id="d4" className="button day" onClick={dayClick} >{repeat_form_d4}</button>
                        <button id="d5" className="button day" onClick={dayClick} >{repeat_form_d5}</button>
                        <button id="d6" className="button day" onClick={dayClick} >{repeat_form_d6}</button>
                        <button id="d7" className="button day" onClick={dayClick} >{repeat_form_d7}</button>
                    </div>
                </div>
                <div className="dropdown-content-separator" />
            </div>
        </div>

        <div className="termin-block-expandable">
            {/* <!-- Task.remind VIEW --> */}
            <div className="termin-block" id="remind-view">
                {/* {{ form.remind.errors }} */}
                <button className="termin-block__content" onClick={toggleSelectField} >
                    <i className="bi-bell termin-block__icon" />
                    <div id="id_remind_title" className="termin-block__title">
                        {item.remind ?
                            <>
                                <div className={extraClass('', item.remindActive, 'actual')}>{item.remindTime}</div>
                                <div className="termin-block__description">{item.remindDate}</div>
                            </> : 
                            <span>To remind</span>
                        }
                    </div>
                </button>
                {item.remind &&
                    <button name="remind_delete" id="id_remind_delete" className="bi-x del-item-icon" onClick={delRemind} />
                }
            </div>


            {/* <!-- Task.remind SELECT --> */}
            <div className="section-item d-none" id="remind-select">
                <div className="dropdown-content-separator" />
                <button className="dropdown-content-item c001" name="remind_today" onClick={remindToday} >
                    <div className="c002">
                        <i className="bi-clock" />
                        <span className="c003">Later</span>
                    </div>
                    <div className="c004">{remindLaterInfo}</div>
                </button>
                <button className="dropdown-content-item c001" name="remind_tomorrow" onClick={remindTomorrow} >
                    <div className="c002">
                        <i className="bi-clock-history" />
                        <span className="c003">Tomorrow</span>
                    </div>
                    <div className="c004">{remindTomorrowInfo}</div>
                </button>
                <button className="dropdown-content-item c001" name="remind_next_week" onClick={remindNextWeek} >
                    <div className="c002">
                        <i className="bi-calendar-week"></i>
                        <span className="c003">Next week</span>
                    </div>
                    <div className="c004">{remindNextWeekInfo}</div>
                </button>
                <div className="section-inner">
                    {item.remind}
                </div>
                <div className="dropdown-content-separator" />
            </div>
        </div>
    </>);
}

export default ItemTermin;