const barColorGradient = [[0xff, 0xc5, 0xbf], [0xf0, 0xf4, 0xc1], [0xbf, 0xd9, 0xff]];
const barColorOpacity = 0.5;
const borderColorGradient = [[0xfd, 0x9e, 0x93], [0xcc, 0xee, 0x95], [0xa0, 0xc6, 0xff]];
const borderColorOpacity = 1;


function getTempColor(temperature: number, border: boolean): string {
    let colorHot: number[], colorZero: number[], colorCold: number[], opacity: number;
    if (border) {
        colorHot = borderColorGradient[0];
        colorZero = borderColorGradient[1];
        colorCold = borderColorGradient[2];
        opacity = borderColorOpacity;
    } else {
        colorHot = barColorGradient[0];
        colorZero = barColorGradient[1];
        colorCold = barColorGradient[2];
        opacity = barColorOpacity;
    }
    let rgb: number[];
    if (temperature == 0)
        rgb = colorZero;
    else {
        let colorTemp, weight;
        if (temperature > 0) {
            colorTemp = colorHot;
            weight = 35 - (temperature > 35 ? 35 : temperature);
        } else {
            colorTemp = colorCold;
            weight = 35 + (temperature < -35 ? -35 : temperature);
        }
        const w1: number = weight / 35;
        var w2 = 1 - w1;
        rgb = [
            Math.round(colorZero[0] * w1 + colorTemp[0] * w2),
            Math.round(colorZero[1] * w1 + colorTemp[1] * w2),
            Math.round(colorZero[2] * w1 + colorTemp[2] * w2)
        ];
    }
    return 'rgba(' + rgb[0] + ', ' + rgb[1] + ', ' + rgb[2] + ', ' + opacity + ')';
}

export interface TempBarHeight {
    maxTemp: string;
    minTemp: string;
    avgTemp: string;
    top: number;
    mid: number;
    color: string;
    borderTop: string;
    borderBot: string;
    precipitation: number;
}

export function getTempBarsInfo(values: any, forWeek: boolean): TempBarHeight[] {
    let ret: TempBarHeight[] = [];
    let maxPeriodValue: number;
    if (forWeek)
        maxPeriodValue = values.map((x: any) => x.temperature_max).reduce(function(prev: number, curr: number) { return prev > curr ? prev : curr; });
    else
        maxPeriodValue = values.map((x: any) => x.temperature).reduce(function(prev: number, curr: number) { return prev > curr ? prev : curr; });
    ret = values.map((day: any) => {
        let maxValue, maxValueStr, minValue, minValueStr, avgValue, avgValueStr, topHeight, midHeight, borderTopColor, borderBotColor;
        if (forWeek) {
            maxValue = Math.round(+day.temperature_max);
            maxValueStr = (maxValue == 0? '' : (maxValue > 0 ? '+' : '-')) + maxValue;
            minValue = Math.round(+day.temperature_min);
            minValueStr = (minValue == 0? '' : (minValue > 0 ? '+' : '-')) + minValue;
            topHeight = 25 + (maxPeriodValue - day.temperature_max) * 2;
            midHeight = 2 * (day.temperature_max - day.temperature_min);
            borderTopColor = getTempColor(day.temperature_max, true);
            borderBotColor = getTempColor(day.temperature_min, true);
        } else {
            avgValue = Math.round(+day.temperature);
            avgValueStr = (avgValue == 0? '' : (avgValue > 0 ? '+' : '-')) + avgValue;
            topHeight = 5 + (maxPeriodValue - day.temperature) * 4;
            midHeight = 25;
            borderTopColor = getTempColor(day.temperature, true);
            borderBotColor = getTempColor(day.temperature, true);
        }

        return {
            maxTemp: maxValueStr,
            minTemp: minValueStr,
            avgTemp: avgValueStr,
            top: topHeight,
            mid: midHeight,
            color: getTempColor(day.temperature, false),
            borderTop: borderTopColor,
            borderBot: borderBotColor,
            precipitation: day.prec_total,
        }
    });
    return ret;
}

export function getIconHref(num: number) {
    return `/static/widgets/weather/${num}.svg`
}

export function getDayColor(dayDate: string) {
    const dt = new Date(dayDate);
    const day = dt.getDay();
    let color = 'blue';
    if (day == 0 || day == 6) {
        color = 'red';
    }
    return color;
}

export function getDayName(dayDate: string) {
    const dt = new Date(dayDate);
    let ret = '??';
    switch (dt.getDay()) {
        case 0: ret = 'Вс'; break;
        case 1: ret = 'Пн'; break;
        case 2: ret = 'Вт'; break;
        case 3: ret = 'Ср'; break;
        case 4: ret = 'Чт'; break;
        case 5: ret = 'Пт'; break;
        case 6: ret = 'Сб'; break;
    }
    return ret;
}

export function getMonthName(month: number): string {
    let ret = '???';
    switch (month) {
        case 0: ret = 'янв'; break;
        case 1: ret = 'фев'; break;
        case 2: ret = 'мар'; break;
        case 3: ret = 'апр'; break;
        case 4: ret = 'май'; break;
        case 5: ret = 'июн'; break;
        case 6: ret = 'июл'; break;
        case 7: ret = 'авг'; break;
        case 8: ret = 'сен'; break;
        case 9: ret = 'окт'; break;
        case 10: ret = 'ноя'; break;
        case 11: ret = 'дек'; break;
    }
    return ret;
}

export function getDayDate(dayDate: string, index: number): string {
    const dt = new Date(dayDate);
    const day = dt.getDate();
    let ret = day.toString();
    if (day == 1 || index == 0) {
        const month = dt.getMonth();
        ret += ' ' + getMonthName(month);
    }
    return ret;
}

export function getHourNum(dayDate: string): number {
    const dt = new Date(dayDate);
    const hour = dt.getHours();
    return hour;
}

export function getHourName(dayDate: string): string {
    let hr = getHourNum(dayDate);
    return hr.toString();
}
