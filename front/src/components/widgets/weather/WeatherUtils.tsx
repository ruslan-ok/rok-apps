
const barColorGradient = [[0xff, 0xc5, 0xbf], [0xf0, 0xf4, 0xc1], [0xbf, 0xd9, 0xff]];
const barColorOpacity = 0.5;
const borderColorGradient = [[0xfd, 0x9e, 0x93], [0xcc, 0xee, 0x95], [0xa0, 0xc6, 0xff]];
const borderColorOpacity = 1;


function getTempColor(temperature: number, border: boolean) {
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
    top: number;
    mid: number;
    color: string;
    borderTop: string;
    borderBot: string;
    precipitation: number;
}

export function getTempBarsInfo(values: any): TempBarHeight[] {
    let ret: TempBarHeight[] = [];
    let maxPeriodValue = values.map((x: any) => x.all_day.temperature_max).reduce(function(prev: number, curr: number) { return prev > curr ? prev : curr; });
    ret = values.map((day: any) => {
        const maxValue = Math.round(+day.all_day.temperature_max);
        const maxValueStr = (maxValue == 0? '' : (maxValue > 0 ? '+' : '-')) + maxValue;
        const minValue = Math.round(+day.all_day.temperature_min);
        const minValueStr = (minValue == 0? '' : (minValue > 0 ? '+' : '-')) + minValue;
        return {
            maxTemp: maxValueStr,
            minTemp: minValueStr,
            top: 25 + (maxPeriodValue - day.all_day.temperature_max) * 2,
            mid: 2 * (day.all_day.temperature_max - day.all_day.temperature_min),
            color: getTempColor(day.all_day.temperature, false),
            borderTop: getTempColor(day.all_day.temperature_max, true),
            borderBot: getTempColor(day.all_day.temperature_min, true),
            precipitation: day.all_day.precipitation.total,
        }
    });
    return ret;
}

export function getIconHref(num: number) {
    return `https://www.meteosource.com/static/img/ico/weather/${num}.svg`
}

export function getDayColor(dayDate: string) {
    const dt = new Date(dayDate);
    const day = dt.getDay();
    let color = 'blue';
    if (day == 5 || day == 6) {
        color = 'red';
    }
    return color;
}

export function getDayName(dayDate: string) {
    const dt = new Date(dayDate);
    let ret = '??';
    switch (dt.getDay()) {
        case 0: ret = 'Пн'; break;
        case 1: ret = 'Вт'; break;
        case 2: ret = 'Ср'; break;
        case 3: ret = 'Чт'; break;
        case 4: ret = 'Пт'; break;
        case 5: ret = 'Сб'; break;
        case 6: ret = 'Вс'; break;
    }
    return ret;
}

export function getMonthName(month: number): string {
    let ret = '???';
    switch (month) {
        case 1: ret = 'янв'; break;
        case 2: ret = 'фев'; break;
        case 3: ret = 'мар'; break;
        case 4: ret = 'апр'; break;
        case 5: ret = 'май'; break;
        case 6: ret = 'июн'; break;
        case 7: ret = 'июл'; break;
        case 8: ret = 'авг'; break;
        case 9: ret = 'сен'; break;
        case 10: ret = 'окт'; break;
        case 11: ret = 'ноя'; break;
        case 12: ret = 'дек'; break;
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

export function getFakeData() {
    return {
        "lat": "54.093709N",
        "lon": "28.295668E",
        "elevation": 179,
        "timezone": "Europe/Minsk",
        "units": "metric",
        "current": {
            "icon": "mostly_cloudy",
            "icon_num": 5,
            "summary": "Mostly cloudy",
            "temperature": 21.8,
            "wind": {
                "speed": 1.7,
                "angle": 290,
                "dir": "WNW"
            },
            "precipitation": {
                "total": 0,
                "type": "null"
            },
            "cloud_cover": 75
        },
        "hourly": null,
        "daily": {
            "data": [
                {
                    "day": "2023-08-27",
                    "weather": "overcast",
                    "icon": 7,
                    "summary": "Fog in the morning, cloudy later. Temperature 18/28 °C.",
                    "all_day": {
                        "weather": "overcast",
                        "icon": 7,
                        "temperature": 22.5,
                        "temperature_min": 17.5,
                        "temperature_max": 27.8,
                        "wind": {
                            "speed": 2,
                            "dir": "W",
                            "angle": 274
                        },
                        "cloud_cover": {
                            "total": 87
                        },
                        "precipitation": {
                            "total": 0,
                            "type": "null"
                        }
                    },
                    "morning": null,
                    "afternoon": null,
                    "evening": null
                },
                {
                    "day": "2023-08-28",
                    "weather": "mostly_cloudy",
                    "icon": 5,
                    "summary": "Mostly cloudy, more clouds in the afternoon. Temperature 18/29 °C.",
                    "all_day": {
                        "weather": "mostly_cloudy",
                        "icon": 5,
                        "temperature": 23,
                        "temperature_min": 18.2,
                        "temperature_max": 29,
                        "wind": {
                            "speed": 3,
                            "dir": "SSW",
                            "angle": 212
                        },
                        "cloud_cover": {
                            "total": 80
                        },
                        "precipitation": {
                            "total": 0.4,
                            "type": "rain"
                        }
                    },
                    "morning": null,
                    "afternoon": null,
                    "evening": null
                },
                {
                    "day": "2023-08-29",
                    "weather": "cloudy",
                    "icon": 6,
                    "summary": "Cloudy, fewer clouds in the afternoon. Temperature 16/26 °C.",
                    "all_day": {
                        "weather": "cloudy",
                        "icon": 6,
                        "temperature": 20.5,
                        "temperature_min": 15.5,
                        "temperature_max": 25.5,
                        "wind": {
                            "speed": 3.5,
                            "dir": "ENE",
                            "angle": 68
                        },
                        "cloud_cover": {
                            "total": 84
                        },
                        "precipitation": {
                            "total": 1.4,
                            "type": "rain"
                        }
                    },
                    "morning": null,
                    "afternoon": null,
                    "evening": null
                },
                {
                    "day": "2023-08-30",
                    "weather": "mostly_cloudy",
                    "icon": 5,
                    "summary": "Mostly cloudy, fewer clouds in the afternoon. Temperature rising to 32 °C. Wind from SE in the afternoon.",
                    "all_day": {
                        "weather": "mostly_cloudy",
                        "icon": 5,
                        "temperature": 24.8,
                        "temperature_min": 20.2,
                        "temperature_max": 31.5,
                        "wind": {
                            "speed": 4.1,
                            "dir": "SSE",
                            "angle": 161
                        },
                        "cloud_cover": {
                            "total": 79
                        },
                        "precipitation": {
                            "total": 0,
                            "type": "null"
                        }
                    },
                    "morning": null,
                    "afternoon": null,
                    "evening": null
                },
                {
                    "day": "2023-08-31",
                    "weather": "psbl_rain",
                    "icon": 12,
                    "summary": "Possible rain changing to mostly cloudy in the afternoon. Temperature falling to 25 °C.",
                    "all_day": {
                        "weather": "psbl_rain",
                        "icon": 12,
                        "temperature": 21.2,
                        "temperature_min": 16.2,
                        "temperature_max": 25,
                        "wind": {
                            "speed": 3.1,
                            "dir": "SSW",
                            "angle": 200
                        },
                        "cloud_cover": {
                            "total": 83
                        },
                        "precipitation": {
                            "total": 2.4,
                            "type": "rain"
                        }
                    },
                    "morning": null,
                    "afternoon": null,
                    "evening": null
                },
                {
                    "day": "2023-09-01",
                    "weather": "partly_sunny",
                    "icon": 4,
                    "summary": "Partly sunny, more clouds in the afternoon. Temperature 14/22 °C.",
                    "all_day": {
                        "weather": "partly_sunny",
                        "icon": 4,
                        "temperature": 17,
                        "temperature_min": 13.8,
                        "temperature_max": 21.5,
                        "wind": {
                            "speed": 2.8,
                            "dir": "NNW",
                            "angle": 342
                        },
                        "cloud_cover": {
                            "total": 60
                        },
                        "precipitation": {
                            "total": 0.2,
                            "type": "rain"
                        }
                    },
                    "morning": null,
                    "afternoon": null,
                    "evening": null
                },
                {
                    "day": "2023-09-02",
                    "weather": "partly_sunny",
                    "icon": 4,
                    "summary": "Partly sunny, fewer clouds in the evening. Temperature 11/21 °C.",
                    "all_day": {
                        "weather": "partly_sunny",
                        "icon": 4,
                        "temperature": 16,
                        "temperature_min": 11.2,
                        "temperature_max": 21,
                        "wind": {
                            "speed": 2.1,
                            "dir": "NNW",
                            "angle": 341
                        },
                        "cloud_cover": {
                            "total": 36
                        },
                        "precipitation": {
                            "total": 0,
                            "type": "null"
                        }
                    },
                    "morning": null,
                    "afternoon": null,
                    "evening": null
                }
            ]
        }
    }
}

