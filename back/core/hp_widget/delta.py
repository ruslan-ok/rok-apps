from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum

class ChartPeriod(Enum):
    p1h = '1h'
    p3h = '3h'
    p12h = '12h'
    p24h = '24h'
    p7d = '7d'
    p30d = '30d'
    p3m = '3m'
    p1y = '1y'
    p3y = '3y'
    p5y = '5y'
    p10y = '10y'

class ChartDataVersion(Enum):
    v1 = 'v1'
    v2 = 'v2'

def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and (not y%100==0 or y%400 == 0) else 28,
        31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d, month=m, year=y)

def yeardelta(date, delta):
    y = (date.year + delta)
    m = date.month
    d = min(date.day, [31,
        29 if y%4==0 and (not y%100==0 or y%400 == 0) else 28,
        31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d, month=m, year=y)

def get_start_date(enddate: datetime, period: ChartPeriod) -> datetime:
    match period:
        case ChartPeriod.p1h: startdate = enddate - timedelta(hours=1)
        case ChartPeriod.p3h: startdate = enddate - timedelta(hours=3)
        case ChartPeriod.p12h: startdate = enddate - timedelta(hours=12)
        case ChartPeriod.p24h: startdate = enddate - timedelta(days=1)
        case ChartPeriod.p7d: startdate = enddate - timedelta(days=7)
        case ChartPeriod.p30d: startdate = monthdelta(enddate, -1)
        case ChartPeriod.p3m: startdate = monthdelta(enddate, -3)
        case ChartPeriod.p1y: startdate = yeardelta(enddate, -1)
        case ChartPeriod.p3y: startdate = yeardelta(enddate, -3)
        case ChartPeriod.p5y: startdate = yeardelta(enddate, -5)
        case ChartPeriod.p10y: startdate = yeardelta(enddate, -10)
    return startdate

# Какие требования к маске преобразования даты в строку:
# 1. Результирующая строка должна быть как меньше короче, иначе график будет выглядеть некрасиво.
# 2. Количество значений за период должно быть в районе 200, но не сильно меньше, иначе график получится слишком дискретный
# 3. Для периодов на пересечении года придется добавлять в шаблон год, чтобы сохранить правильную сортировку - а может и нет
def get_date_mask(period: ChartPeriod) -> str:
    match period:
        case ChartPeriod.p1h:  x_mask = '%H:%M'    # 60
        case ChartPeriod.p3h:  x_mask = '%H:%M'    # 180
        case ChartPeriod.p12h: x_mask = '%H:%M'    # 720
        case ChartPeriod.p24h: x_mask = '%H:%M'    # 1440
        case ChartPeriod.p7d:  x_mask = '%d %H'    # 168
        case ChartPeriod.p30d: x_mask = '%d %H'    # 720
        case ChartPeriod.p3m:  x_mask = '%m.%d %H' # 2160
        case ChartPeriod.p1y:  x_mask = '%y.%m.%d' # 365
        case ChartPeriod.p3y:  x_mask = '%y.%m.%d' # 1080
        case ChartPeriod.p5y:  x_mask = '%y.%m.%d' # 1800
        case ChartPeriod.p10y: x_mask = '%y.%m.%d' # 3650
    return x_mask

@dataclass
class SourceData:
    event: datetime
    value: Decimal

def approximate(period: ChartPeriod, data: list[SourceData], goal: int) -> list:
    ret = []
    x_mask = get_date_mask(period)
    cur_time = None
    average: Decimal = Decimal(0)
    qty: int = 0
    skiper = int(len(data) / goal)
    if not skiper:
        return [{'x': item.event.strftime(x_mask), 'y': item.value} for item in data]
    for ndx, item in enumerate(data):
        if not cur_time:
            cur_time = item.event
            average = Decimal(0)
            qty = 0
        if item.value:
            average += Decimal(item.value)
            qty += 1
        if ndx % skiper == 0 and qty:
            ret.append({ 'x': cur_time.strftime(x_mask), 'y': average / qty })
            cur_time = None
    return ret
