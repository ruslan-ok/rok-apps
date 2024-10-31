import { SubGroupKind } from './SubGroup';

export class IDateTime {
    dt: Date;

    constructor(s: string | null = null) {
        if (s)
            this.dt = new Date(s);
        else
            this.dt = new Date();
    }

    get year(): number {
        return +this.dt.toISOString().split('T')[0].split('-')[0];
    }

    get month(): number {
        return +this.dt.toISOString().split('T')[0].split('-')[1];
    }

    get day(): number {
        return +this.dt.toISOString().split('T')[0].split('-')[2];
    }

    get hours(): number {
        return +this.dt.toISOString().split('T')[1].split(':')[0];
    }

    get minutes(): number {
        return +this.dt.toISOString().split('T')[1].split(':')[1];
    }

    get seconds(): number {
        return +this.dt.toISOString().split('T')[1].split(':')[2];
    }

    get week(): number {
        const d = new Date(Date.UTC(this.dt.getFullYear(), this.dt.getMonth(), this.dt.getDate()));
        d.setUTCDate(this.dt.getUTCDate() + 4 - (this.dt.getUTCDay()||7));
        var yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
        var weekNo = Math.ceil(( ( (d.valueOf() - yearStart.valueOf()) / 86400000) + 1) / 7);
        return weekNo;
    }

    get dow(): number {
        return this.dt.getUTCDay();
    }

    get value() {
        return this.dt.valueOf();
    }

    get Year(): string {
        return this.year.toString();
    }

    get Month(): string {
        return this.month.toString();
    }

    get Day(): string {
        return this.day.toString();
    }

    get Hours(): string {
        return this.hours.toString();
    }

    get Minutes(): string {
        return this.minutes.toString();
    }

    get Seconds(): string {
        return this.seconds.toString();
    }

    get Dow(): string {
        switch (this.dow) {
            case 0: return 'Sun';
            case 1: return 'Mot';
            case 2: return 'Tue';
            case 3: return 'Wed';
            case 4: return 'Thu';
            case 5: return 'Fri';
            case 6: return 'Sat';
        }
        return '???';
    }

    get Mon(): string {
        switch (this.month) {
            case 1: return 'Jan';
            case 2: return 'Feb';
            case 3: return 'Mar';
            case 4: return 'Apr';
            case 5: return 'Maj';
            case 6: return 'Jun';
            case 7: return 'Jul';
            case 8: return 'Aug';
            case 9: return 'Sep';
            case 10: return 'Oct';
            case 11: return 'Nov';
            case 12: return 'Dec';
        }
        return '???';
    }

    strftime(format: string): string {
        return format.replace('%Y', this.Year).replace('%m', this.Month).replace('%b', this.Mon).replace('%d', this.Day).replace('%M', this.Minutes).replace('%H', this.Hours).replace('%S', this.Seconds);
    }

    date_format(format: string): string {
        return format.replace('D', this.Dow).replace('d', this.Day).replace('N', this.Mon).replace('Y', this.Year).replace('H', this.Hours).replace('i', this.Minutes);
    }
}

enum TerminKind {
    LONG_TIME = 20, // Совсем давно
    LAST_MONTH = 19, // В прошлом месяце
    THREE_WEEKS = 18, // Три недели назад
    TWO_WEEKS = 17, // Две недели назад
    LAST_WEEK = 16, // На прошлой неделе
    MON = 15, // Понедельник
    TUE = 14, // Вторник
    WED = 13, // Среда
    THU = 12, // Четверг
    FRI = 11, // Пятница
    SAT = 10, // Суббота
    SUN = 9, // Воскресенье
    YESTERDAY = 8, // Вчера
    TODAY = 7, // Сегодня
    TOMORROW = 6, // Завтра
    THIS_WEEK = 5, // На этой неделе
    NEXT_WEEK = 4, // На следующей неделе
    THIS_MONTH = 3, // В этом месяце
    NEXT_MONTH = 2, // В следующем месяце
    MUCH_LATER = 1, // Позже, чем через месяц
    ALL = 0, // Все сроки
}

class ITermin {
    sdt: string | null;

    constructor(s: string | null) {
        this.sdt = s;
    }

    get dt() {
        return new IDateTime(this.sdt);
    }

    get days(): number | null {
        let termin = null;
        if (this.sdt) {
            const today = new IDateTime();
            const dateDiff: number = this.dt.value - today.value;
            termin = Math.round((dateDiff) / (1000 * 60 * 60 * 24));
        }
        return termin;
    }

    get months(): number | null {
        if (!this.dt)
            return null;
        const today = new IDateTime();
        return this.years ? (this.years * 12 + this.dt.month - today.month) : null;
    }

    get years(): number | null {
        if (!this.dt)
            return null;
        const today = new IDateTime();
        return (this.dt.year - today.year);
    }

    get is_expired(): boolean {
        if (this.dt === null)
            return false;

        const today = new IDateTime();
        if (this.dt.value < today.value)
            return (this.dt.year !== today.year) || (this.dt.month !== today.month) || (this.dt.day !== today.day) || (!this.dt.hours && !this.dt.minutes);

        return false;
    }

    get is_actual(): boolean {
        if (this.dt === null)
            return false;

        const today = new IDateTime();
        if (this.dt.value > today.value || (this.dt.year === today.year && this.dt.month === today.month && this.dt.day === today.day && !this.dt.hours && !this.dt.minutes))
            return true;

        return false;
    }

    get kind(): TerminKind {
        if (!this.dt)
            return TerminKind.ALL;

        switch (this.days) {
            case -1: return TerminKind.YESTERDAY;
            case 0: return TerminKind.TODAY;
            case 1: return TerminKind.TOMORROW;
        }

        const today = new IDateTime();

        if (this.dt.year === today.year) {
            const weeks = this.dt.week - today.week;
            switch (weeks) {
                case -1: return TerminKind.LAST_WEEK;
                case 0: return TerminKind.THIS_WEEK;
                case 1: switch(this.dt.dow) {
                    case 0: return TerminKind.SUN;
                    case 1: return TerminKind.MON;
                    case 2: return TerminKind.TUE;
                    case 3: return TerminKind.WED;
                    case 4: return TerminKind.THU;
                    case 5: return TerminKind.FRI;
                    case 6: return TerminKind.SAT;
                };
            }
        }

        switch (this.months) {
            case -1: return TerminKind.LAST_MONTH;
            case 0: return TerminKind.THIS_MONTH;
            case 1: return TerminKind.NEXT_MONTH;
            case 2: return TerminKind.TWO_WEEKS;
            case 3: return TerminKind.THREE_WEEKS;
        }

        if (this.months && this.months > 1)
            return TerminKind.MUCH_LATER;

        return TerminKind.LONG_TIME;
    }
}

const NONE = 0;
const DAILY = 1;
const WORKDAYS = 2;
const WEEKLY = 3;
const MONTHLY = 4;
const ANNUALLY = 5;

const REPEAT = [
    [NONE, 'No'],
    [DAILY, 'Daily'],
    [WORKDAYS, 'Work days'],
    [WEEKLY, 'Weekly'],
    [MONTHLY, 'Monthly'],
    [ANNUALLY, 'Annually']
];

const REPEAT_NAME = {
    [DAILY]: 'days',
    [WEEKLY]: 'weeks',
    [MONTHLY]: 'months',
    [ANNUALLY]: 'years'
};

export interface IGroup {
    id: number;
    name: string;
}

export interface IStep {
    id: number;
    name: string;
    completed: boolean;
}

export interface IFile {
    id: number;
    name: string;
    href: string;
    ext: string;
    size: number;
}

export interface ILink {
    id: number;
    name: string;
}

export class IItemInfo {
    categories: string | null;
    completed: boolean;
    completion: string | null;
    created: string | null;
    event: string | null;
    id: number | null;
    important: boolean;
    in_my_day: boolean;
    info: string | null;
    last_mod: string | null;
    last_remind: string | null;
    name: string;
    remind: string | null;
    repeat: number | null;
    repeat_days: number | null;
    repeat_num: number | null;
    start: string | null;
    stop: string | null;
    steps: IStep[];
    links: ILink[];
    files: IFile[];
    groups: IGroup[];

    constructor(values: Object) {
        this.categories = values.categories;
        this.completed = values?.completed;
        this.completion = values?.completion;
        this.created = values?.created;
        this.event = values?.event;
        this.id = values?.id;
        this.important = values?.important;
        this.in_my_day = values?.in_my_day || false;
        this.info = values?.info;
        this.last_mod = values?.last_mod;
        this.last_remind = values?.last_remind;
        this.name = values?.name || '';
        this.remind = values?.remind;
        this.repeat = values?.repeat;
        this.repeat_days = values?.repeat_days;
        this.repeat_num = values?.repeat_num;
        this.start = values?.start;
        this.stop = values?.stop;
        this.steps = values?.steps || [];
        this.links = values?.links || [];
        this.files = values?.files || [];
        this.groups = values?.groups || [];
    }

    get sub_group_id(): SubGroupKind {
        let sgId = SubGroupKind.UNKNOWN;
        if (this.completed)
            sgId = SubGroupKind.COMPLETED;
        else {
            const termin = new ITermin(this.stop).days;
            if (termin === null)
                sgId = SubGroupKind.UNKNOWN;
            else if (termin < 0)
                sgId = SubGroupKind.EXPIRED;
            else if (termin === 0)
                sgId = SubGroupKind.TODAY;
            else if (termin === 1)
                sgId = SubGroupKind.TOMORROW;
            else if (termin < 8)
                sgId = SubGroupKind.THIS_WEEK;
            else
                sgId = SubGroupKind.LATER;
        } 
        return sgId;
    }

    get termin(): ITermin {
        return new ITermin(this.stop);
    }

    get Completion(): string {
        if (!this.completion)
            return '';
        const compl = new IDateTime(this.completion);
        return compl.strftime('%d.%m.%Y');
    }

    get is_expired(): boolean {
        if (this.completed)
            return false;

        return this.termin.is_expired;
    }

    get is_actual(): boolean {
        if (this.completed)
            return false;

        return this.termin.is_actual;
    }

    get _only_nice_date(): string {
        let ret = '';
        if (this.termin) {
            switch (this.termin.kind) {
                case TerminKind.TODAY: ret = 'Today'; break;
                case TerminKind.TOMORROW: ret = 'Tomorrow'; break;
                case TerminKind.YESTERDAY: ret = 'Yesterday'; break;
            }
        }
        if (this.termin.dt.hours || this.termin.dt.minutes)
            ret += this.termin.dt.strftime(' %H:%M');
        return ret;
    }

    get nice_date(): string {
        let ret = this._only_nice_date;
        if (ret)
            return ret

        if (!this.termin.dt.hours && !this.termin.dt.minutes) {
            if (!this.termin.years)
                ret = this.termin.dt.date_format('D, d N');
            else
                ret = this.termin.dt.date_format('D, d N Y');
        } else {
            if (!this.termin.years)
                ret = this.termin.dt.date_format('D, d N H:i');
            else
                ret = this.termin.dt.date_format('D, d N Y H:i');
        }
        
        return ret;
    
    }

    get termin_info(): string {
        if (!this.stop)
            return '';
        let label = this.is_expired ? 'Expired, ' : 'Termin: ';
        return label + this.nice_date;
    }

    get s_repeat(): string {
        if (!this.repeat || this.repeat === NONE) return '';

        if (this.repeat_num === 1) {
            return this.repeat === WORKDAYS 
                ? '' + REPEAT[WEEKLY][1]
                : '' + REPEAT[this.repeat][1];
        }

        const repeatName = this.repeat ? REPEAT_NAME[this.repeat]: '';
        return `Once every ${this.repeat_num} ${repeatName}`;
    }

    get repeat_s_days(): string {
        if (this.repeat === WEEKLY) {
            if (this.repeat_days === 0) {
                const start = this.start ? new Date(this.start) : null;
                const stop = this.stop ? new Date(this.stop) : null;
                const ddd = stop || start;
                if (ddd) {
                    return this.weekDayName(ddd);
                }
                return '???';
            }

            if (this.repeat_days === (1 + 2 + 4 + 8 + 16)) {
                return 'Work days';
            }

            let ret = '';
            const monday = new Date(2020, 6, 6); // July 6, 2020 is a Monday

            for (let i = 0; i < 7; i++) {
                if (this.repeat_days || 0 & (1 << i)) {
                    if (ret) ret += ', ';
                    ret += this.weekDayName(new Date(monday.getTime() + i * 86400000));
                }
            }
            return ret;
        }
        return '';
    }

    getWeekDayName(weekday_num: number): string {
        const d = new Date('2020-07-13');
        if (weekday_num > 1)
            d.setDate(d.getDate() + weekday_num - 1);
        return this.weekDayName(d);
    }
    
    // Format date to the abbreviated day of the week
    weekDayName(date: Date) {
        const options: Intl.DateTimeFormatOptions = { weekday: 'short' };
        return new Intl.DateTimeFormat('en-GB', options).format(date);
    }

    get remindActive(): boolean {
        const cond1: boolean = this.remind !== null;
        const cond2: boolean = !this.completed;
        const d1 = new Date(this.remind || '');
        const d2 = new Date();
        const cond3: boolean = d1 > d2;
        return cond1 && cond2 && cond3;
    }

    get remindTime(): string {
        if (this.remind === null)
            return '';
        const remindTime = new IDateTime(this.remind);
        return 'Remind in ' + remindTime.strftime('%H:%M');
    }

    get remindDate(): string {
        if (this.remind === null)
            return '';
        let ret = '';
        const remindTime = new ITermin(this.remind);
        if (!remindTime.dt.hours && !remindTime.dt.minutes) {
            if (!remindTime.years)
                ret = remindTime.dt.date_format('D, d N');
            else
                ret = remindTime.dt.date_format('D, d N Y');
        } else {
            if (!this.termin.years)
                ret = remindTime.dt.date_format('D, d N H:i');
            else
                ret = remindTime.dt.date_format('D, d N Y H:i');
        }
        
        return ret;
    }
}

// ========================================================
// Extra

interface IItemRole {
    href: string;
    hide_params: boolean;
    icon: string;
    params: string;
    name_mod: string;
}

interface IAttrInfo {
    icon: string;
}

export interface ITodoExtra {
    initialized: boolean;
    roles: IItemRole[];
    params: string;
    group_name: string | null;
    attributes: IAttrInfo[];
    remind_active: boolean;
    step_completed: number;
    step_total: number;
    has_files: boolean;
    has_links: boolean;
    task_descr: string;
}

