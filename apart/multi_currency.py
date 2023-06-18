from task.models import Task
from task.const import NUM_ROLE_METER_VALUE, NUM_ROLE_METER_PROP, NUM_ROLE_SERV_VALUE, NUM_ROLE_SERV_PROP, NUM_ROLE_APART, NUM_ROLE_METER, NUM_ROLE_BILL
from apart.calc_tarif import HSC, INTERNET, PHONE, get_bill_info

def apart_check_meter_prop(user, apart, prop, code) -> int:
    if prop:
        Task.objects.create(user=user, app_apart=NUM_ROLE_METER_PROP, task_1=apart, name=code)
        return 1
    return 0

def apart_check_serv_prop(user, apart, prop, code) -> int:
    if prop:
        Task.objects.create(user=user, app_apart=NUM_ROLE_SERV_PROP, task_1=apart, name=code)
        return 1
    return 0

def apart_check_meters(user, apart) -> int:
    ret = 0
    for meter in Task.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id):
        if apart.apart_has_el:
            meter.id = None
            meter.app_apart = NUM_ROLE_METER_VALUE
            meter.name = 'el_meter'
            meter.meter_zkx = meter.meter_el
            meter.save()
            ret += 1
        if apart.apart_has_hw:
            meter.id = None
            meter.app_apart = NUM_ROLE_METER_VALUE
            meter.name = 'hw_meter'
            meter.meter_zkx = meter.meter_hw
            meter.save()
            ret += 1
        if apart.apart_has_cw:
            meter.id = None
            meter.app_apart = NUM_ROLE_METER_VALUE
            meter.name = 'cw_meter'
            meter.meter_zkx = meter.meter_cw
            meter.save()
            ret += 1
        if apart.apart_has_gas:
            meter.id = None
            meter.app_apart = NUM_ROLE_METER_VALUE
            meter.name = 'gas_meter'
            meter.meter_zkx = meter.meter_ga
            meter.save()
            ret += 1
    return ret

def ins_service(bill, code, used, tariff, accrued, payment):
    if used:
        bill.id = None
        bill.app_apart = NUM_ROLE_SERV_VALUE
        bill.name = code
        bill.price_tarif = tariff
        bill.bill_tv_bill = accrued
        bill.bill_tv_pay = payment
        bill.save()
        return 1
    return 0
   
def apart_check_services(user, apart) -> int:
    ret = 0
    for bill in Task.objects.filter(user=user.id, app_apart=NUM_ROLE_BILL, task_1=apart.id):
        if bill.task_2 and bill.task_3:
            bill_info = get_bill_info(bill)
            ret += ins_service(bill, code='internet', used=bill_info['internet']['used'], tariff=None, accrued=bill.bill_tv_bill, payment=bill.bill_tv_pay)
            ret += ins_service(bill, code='phone', used=bill_info['phone']['used'] and apart.name in ['Лесной'], tariff=None, accrued=bill.bill_phone_bill, payment=bill.bill_phone_pay)
            ret += ins_service(bill, code='mobile', used=bill_info['phone']['used'] and apart.name in ['Wrocław', 'Жодино'], tariff=None, accrued=bill.bill_phone_bill, payment=bill.bill_phone_pay)
            ret += ins_service(bill, code='zkx', used=bill_info['zkx']['used'] and apart.name in ['Жодино'], tariff=None, accrued=bill.bill_zhirovka, payment=bill.bill_zkx_pay)
            ret += ins_service(bill, code='parking', used=bill_info['zkx']['used'] and apart.name in ['Wrocław'], tariff=None, accrued=bill.bill_zhirovka, payment=bill.bill_zkx_pay)
            ret += ins_service(bill, code='ppo', used=bill_info['poo']['used'] and apart.name in ['Лесной'], tariff=None, accrued=bill.bill_poo, payment=bill.bill_poo_pay)
            ret += ins_service(bill, code='rent', used=bill_info['poo']['used'] and apart.name in ['Wrocław'], tariff=None, accrued=bill.bill_poo, payment=bill.bill_poo_pay)
            ret += ins_service(bill, code='el_supply', used=bill_info['electro']['used'], tariff=bill_info['electro']['tarif'], accrued=None, payment=bill.bill_el_pay)
            ret += ins_service(bill, code='gas_supply', used=bill_info['gas']['used'], tariff=bill_info['gas']['tarif'], accrued=None, payment=bill.bill_gas_pay)
            ret += ins_service(bill, code='water_supply', used=bill_info['water']['used'], tariff=bill_info['water']['tarif'], accrued=None, payment=bill.bill_water_pay)
    return ret

def multi_currency_init(user):
    Task.objects.filter(app_apart=NUM_ROLE_METER_VALUE).delete()
    Task.objects.filter(app_apart=NUM_ROLE_METER_PROP).delete()
    Task.objects.filter(app_apart=NUM_ROLE_SERV_VALUE).delete()
    Task.objects.filter(app_apart=NUM_ROLE_SERV_PROP).delete()
    upd_apart = ins_meter_prop = ins_meter_value = ins_serv_prop = ins_serv_value = 0
    for apart in Task.objects.filter(app_apart=NUM_ROLE_APART):
        upd_apart += 1
        
        ins_meter_prop += apart_check_meter_prop(user, apart, apart.apart_has_gas, 'gas_meter')
        ins_meter_prop += apart_check_meter_prop(user, apart, apart.apart_has_el, 'el_meter')
        ins_meter_prop += apart_check_meter_prop(user, apart, apart.apart_has_hw, 'hw_meter')
        ins_meter_prop += apart_check_meter_prop(user, apart, apart.apart_has_cw, 'cw_meter')
        
        ins_serv_prop += apart_check_serv_prop(user, apart, apart.apart_has_gas, 'gas_supply')
        ins_serv_prop += apart_check_serv_prop(user, apart, apart.apart_has_el, 'el_supply')
        ins_serv_prop += apart_check_serv_prop(user, apart, apart.apart_has_cw, 'water_supply')
        ins_serv_prop += apart_check_serv_prop(user, apart, apart.apart_has_cw, 'sewerage')
        ins_serv_prop += apart_check_serv_prop(user, apart, apart.apart_has_tv, 'tv')
        ins_serv_prop += apart_check_serv_prop(user, apart, apart.apart_has_phone, 'phone')
        ins_serv_prop += apart_check_serv_prop(user, apart, apart.apart_has_zkx, 'zkx')
        ins_serv_prop += apart_check_serv_prop(user, apart, apart.apart_has_ppo, 'ppo')
        
        ins_meter_value += apart_check_meters(user, apart)
        ins_serv_value += apart_check_services(user, apart)
    
    return {'result': 'ok', 'upd_apart': upd_apart, 'ins_meter_prop': ins_meter_prop, 'ins_meter_value': ins_meter_value, 'ins_serv_prop': ins_serv_prop, 'ins_serv_value': ins_serv_value, }

