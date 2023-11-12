APART_METER = {
    'el_meter': 'электричество',
    'cw_meter': 'холодная вода',
    'hw_meter': 'горячая вода',
    'ht_meter': 'тепловая энергия',
    'gas_meter': 'газ',
}

ELECTRICITY = 1
GAS = 2
WATER = 3
WATER_SUPPLY = 4
SEWERAGE = 5
NOT_SET = 6
ELECTRICITY_2 = 7
LAND_TAX = 8
TV = 9
INTERNET = 10
PHONE = 11
COLD_WATER = 20
HOT_WATER = 21
HSC = 22
POO = 23
MOBILE = 31
RENT = 32
PARKING = 33
GARAGE = 34
GARBAGE = 35

APART_SERVICE = {
    'el_supply': (ELECTRICITY, 'электроснабжение'),
    'gas_supply': (GAS, 'газоснабжение'),
    'water_supply': (WATER_SUPPLY, 'водоснабжение'),
    'sewerage': (SEWERAGE, 'водоотведение'),
    'internet': (INTERNET, 'интернет'),
    'tv': (TV, 'телевидение'),
    'phone': (PHONE, 'стационарный (городской) телефон'),
    'mobile': (MOBILE, 'мобильный телефон'),
    'zkx': (HSC, 'жилищно-коммунальные услуги'),
    'ppo': (POO, 'платежи товариществу собственников'),
    'rent': (RENT, 'арендная плата'),
    'parking': (PARKING, 'аренда парковки'),
    'garage_fee': (GARAGE, 'членские взносы в гаражный кооператив'),
    'garbage': (GARBAGE, 'вывоз мусора'),
}

def apart_service_name_by_id(id: int) -> str:
    service_name = '???'
    for k, v in APART_SERVICE.items():
        if v[0] == id:
            service_name = v[1]
            break
    return service_name

