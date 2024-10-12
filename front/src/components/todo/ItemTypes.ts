import { SubGroupKind } from './SubGroup';

class DateTime {
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
        return format.replace('%Y', this.Year).replace('%m', this.Month).replace('%d', this.Day).replace('%M', this.Minutes).replace('%H', this.Hours).replace('%S', this.Seconds);
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

class Termin {
    sdt: string | null;

    constructor(s: string | null) {
        this.sdt = s;
    }

    get dt() {
        return new DateTime(this.sdt);
    }

    get days(): number | null {
        let termin = null;
        if (this.sdt) {
            const today = new DateTime();
            const dateDiff: number = this.dt.value - today.value;
            termin = Math.round((dateDiff) / (1000 * 60 * 60 * 24));
        }
        return termin;
    }

    get months(): number | null {
        if (!this.dt)
            return null;
        const today = new DateTime();
        return this.years ? (this.years * 12 + this.dt.month - today.month) : null;
    }

    get years(): number | null {
        if (!this.dt)
            return null;
        const today = new DateTime();
        return (this.dt.year - today.year);
    }

    get is_expired(): boolean {
        if (this.dt === null)
            return false;

        const today = new DateTime();
        if (this.dt.value < today.value)
            return (this.dt.year !== today.year) || (this.dt.month !== today.month) || (this.dt.day !== today.day) || (!this.dt.hours && !this.dt.minutes);

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

        const today = new DateTime();

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

export class ItemInfo {
    categories: string | null;
    completed: boolean | null;
    completion: string | null;
    created: string | null;
    event: string | null;
    groups: number[] | null;
    id: number;
    important: boolean | null;
    in_my_day: boolean | null;
    info: string | null;
    last_mod: string | null;
    last_remind: string | null;
    name: string | null;
    remind: string | null;
    repeat: number | null;
    repeat_days: number | null;
    repeat_num: number | null;
    start: string | null;
    stop: string | null;

    constructor(values: Object) {
        this.categories = values.categories;
        this.completed = values?.completed;
        this.completion = values?.completion;
        this.created = values?.created;
        this.event = values?.event;
        this.groups = values?.groups;
        this.id = values?.id;
        this.important = values?.important;
        this.in_my_day = values?.in_my_day;
        this.info = values?.info;
        this.last_mod = values?.last_mod;
        this.last_remind = values?.last_remind;
        this.name = values?.name;
        this.remind = values?.remind;
        this.repeat = values?.repeat;
        this.repeat_days = values?.repeat_days;
        this.repeat_num = values?.repeat_num;
        this.start = values?.start;
        this.stop = values?.stop;
    }

    get sub_group_id(): SubGroupKind {
        let sgId = SubGroupKind.UNKNOWN;
        if (this.completed)
            sgId = SubGroupKind.COMPLETED;
        else {
            const termin = new Termin(this.stop).days;
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

    get termin(): Termin {
        return new Termin(this.stop);
    }

    get Completion(): string {
        if (!this.completion)
            return '';
        const compl = new DateTime(this.completion);
        return compl.strftime('%d.%m.%Y');
    }

    get is_expired(): boolean {
        if (this.completed)
            return false;

        return this.termin.is_expired;
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
            return 'Set due date';
        let label = this.is_expired ? 'Expired, ' : 'Termin: ';
        return label + this.nice_date;
    }
}

interface ItemRole {
    href: string;
    hide_params: boolean;
    icon: string;
    params: string;
    name_mod: string;
}

interface AttrInfo {
    icon: string;
}

export interface ExtraInfo {
    roles: ItemRole[];
    absolute_url: string;
    params: string;
    group_name: string | null;
    attributes: AttrInfo[];
    remind_active: boolean;
    step_completed: number;
    step_total: number;
}
