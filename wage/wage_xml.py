import xml.etree.ElementTree as ET
from datetime import datetime
from .models import Period, Depart, DepHist, Post, Person, FioHist, Child, Appoint, Education, PersPer, PayTitle, Payment

id_depart = {}
id_post = {}

def GetStr(attr, name):
    if attr.get('{rok}' + name):
        return attr.get('{rok}' + name)
    return ''

def GetInt(attr, name):
    if attr.get('{rok}' + name):
        return int(attr.get('{rok}' + name))
    return 0

def GetFloat(attr, name):
    if attr.get('{rok}' + name):
        return float(attr.get('{rok}' + name))
    return 0

def GetDate(attr, name):
    if attr.get('{rok}' + name):
        return datetime.strptime(attr.get('{rok}' + name), '%d/%m/%Y')
    return None

def GetPeriod(attr, name, err):
    xml_id = GetStr(attr, name)
    if (xml_id == ''):
        return None
    y = (int(xml_id) // 12) + 2009
    m = (int(xml_id) % 12) + 1
    d = datetime(y, m, 1)
    return Period.objects.get(dBeg=d)

def GetDepart(attr, name, err):
    xml_id = GetStr(attr, name)
    if (xml_id == ''):
        return None

    mem_id = id_depart.get(xml_id)
    if (mem_id == None):
        err.append('Битая ссылка на Depart: ' + xml_id)
        return None

    return Depart.objects.get(id=mem_id)

def GetPost(attr, name, err):
    xml_id = GetStr(attr, name)
    if (xml_id == ''):
        return None

    mem_id = id_post.get(xml_id)
    if (mem_id == None):
        err.append('Битая ссылка на Post: ' + xml_id)
        return None

    return Post.objects.get(id=mem_id)

def GetPayTitle(attr, name, err):
    xml_id = GetStr(attr, name)
    if (xml_id == ''):
        return None
    return PayTitle.objects.get(id=(int(xml_id)+3))

def import_period(n, cnt, err):
    p = Period.objects.create(dBeg = GetDate(n.attrib, 'dBeg'), planDays = 22)
    p.planDays = GetInt(n.attrib, 'PlanDays')
    p.AvansDate = GetDate(n.attrib, 'AvansDate')
    p.PaymentDate = GetDate(n.attrib, 'PaymentDate')
    p.AvansRate = GetFloat(n.attrib, 'AvansRate')
    p.PaymentRate = GetFloat(n.attrib, 'PaymentRate')
    p.DebtInRate = GetFloat(n.attrib, 'DebtInRate')
    p.Part2Date = GetDate(n.attrib, 'Part2Date')
    p.Part2Rate = GetFloat(n.attrib, 'Part2Rate')
    p.save()
    cnt.append('Period:' + p.__str__())

def import_depart(n, cnt, err):
    r = Depart.objects.create()
    r.name = GetStr(n.attrib, 'Name')
    r.sort = GetStr(n.attrib, 'Sort')
    r.save()
    xml_id = str(GetInt(n.attrib, 'Id'))
    id_depart[xml_id] = r.id
    #err.append(xml_id + ': ' + str(id_depart[xml_id]))
    cnt.append('Depart:' + r.__str__())

def import_dephist(n, cnt, err):
    did = GetDepart(n.attrib, 'Depart', err)
    if (did == None):
        return
    r = DepHist.objects.create(depart=did)
    r.dBeg = GetDate(n.attrib, 'dBeg')
    r.dEnd = GetDate(n.attrib, 'dEnd')
    r.sort = GetStr(n.attrib, 'Sort')
    nid = GetDepart(n.attrib, 'Node', err)
    if (nid != None):
        r.node = nid
    r.save()
    cnt.append('DepHist:' + r.__str__())

def import_post(n, cnt, err):
    r = Post.objects.create()
    r.name = GetStr(n.attrib, 'Name')
    r.save()
    xml_id = str(GetInt(n.attrib, 'Id'))
    id_post[xml_id] = r.id
    cnt.append('Post:' + r.__str__())

def import_fiohist(pers, n, cnt, err):
    r = FioHist.objects.create(person=pers)
    r.fio = GetStr(n.attrib, 'FIO')
    r.dEnd = GetDate(n.attrib, 'dEnd')
    r.info = GetStr(n.attrib, 'Info')
    r.save()
    cnt.append('FioHist:' + r.__str__())

def import_child(pers, n, cnt, err):
    r = Child.objects.create(person=pers)
    r.born = GetDate(n.attrib, 'Born')
    r.sort = GetStr(n.attrib, 'Num')
    r.name = GetStr(n.attrib, 'Name')
    r.info = GetStr(n.attrib, 'Info')
    r.save()
    cnt.append('Child:' + r.__str__())

def import_appoint(pers, n, cnt, err):
    did = GetDepart(n.attrib, 'Depart', err)
    if (did == None):
        return
    r = Appoint.objects.create(person=pers, depart=did)
    r.tabnum = GetStr(n.attrib, 'TabNum')
    r.dBeg = GetDate(n.attrib, 'dBeg')
    r.dEnd = GetDate(n.attrib, 'dEnd')
    r.salary = GetFloat(n.attrib, 'Salary')
    r.currency = GetStr(n.attrib, 'Currency')
    r.taxded = GetFloat(n.attrib, 'TaxDed')
    r.info = GetStr(n.attrib, 'Info')
    pid = GetPost(n.attrib, 'Post', err)
    if (pid != None):
        r.post = pid
    r.save()
    cnt.append('Appoint:' + r.__str__())


def import_education(pers, n, cnt, err):
    r = Education.objects.create(person=pers)
    r.dBeg = GetDate(n.attrib, 'dBeg')
    r.dEnd = GetDate(n.attrib, 'dEnd')
    r.institution = GetStr(n.attrib, 'Institution')
    r.course = GetStr(n.attrib, 'Course')
    r.specialty = GetStr(n.attrib, 'Specialty')
    r.qualification = GetStr(n.attrib, 'Qualification')
    r.document = GetStr(n.attrib, 'Document')
    r.number = GetStr(n.attrib, 'Number')
    r.city = GetStr(n.attrib, 'City')
    r.docdate = GetDate(n.attrib, 'DocDate')
    r.info = GetStr(n.attrib, 'Info')
    r.save()
    cnt.append('Education:' + r.__str__())

def import_payment(pers, per, dir, n, cnt, err):
    tid = GetPayTitle(n.attrib, 'Title', err)
    if (tid == None):
        return
    r = Payment.objects.create(person=pers, period=per, title=tid, direct=dir)
    r.payed = GetDate(n.attrib, 'Payed')
    r.sort = GetStr(n.attrib, 'Sort')
    r.value = GetFloat(n.attrib, 'Value')
    r.currency = GetStr(n.attrib, 'Currency')
    r.rate = GetFloat(n.attrib, 'Rate')
    r.info = GetStr(n.attrib, 'Info')
    r.save()
    cnt.append('Payment:' + r.__str__())

def import_persper(pers, n, cnt, err):
    pid = GetPeriod(n.attrib, 'Period', err)
    if (pid == None):
        return
    r = PersPer.objects.create(person=pers, period=pid)
    r.factDays = GetFloat(n.attrib, 'FactDays')
    r.debtIn = GetFloat(n.attrib, 'DebtIn')
    r.debtOut = GetFloat(n.attrib, 'DebtOut')
    r.salaryRate = GetFloat(n.attrib, 'SalaryRate')
    r.privilege = GetFloat(n.attrib, 'Privilege')
    r.save()
    cnt.append('PersPer:' + r.__str__())
    for p in n:
        if (p.tag == '{rok}Nachisl'):
            import_payment(pers, r.period, 0, p, cnt, err)
        elif (p.tag == '{rok}Payment'):
            import_payment(pers, r.period, 1, p, cnt, err)
        else:
            err.append('[x] unexpected tag [import_persper]:' + p.tag.__str__())

def import_person(n, cnt, err):
    r = Person.objects.create()
    r.fio = GetStr(n.attrib, 'FIO')
    r.login = GetStr(n.attrib, 'Login')
    r.sort = GetStr(n.attrib, 'Sort')
    r.email = GetStr(n.attrib, 'EMail')
    r.passw = GetStr(n.attrib, 'Passw')
    r.born = GetDate(n.attrib, 'Born')
    r.phone = GetStr(n.attrib, 'Phone')
    r.addr = GetStr(n.attrib, 'Addr')
    r.info = GetStr(n.attrib, 'Info')
    r.save()
    cnt.append('Person:' + r.__str__())
    for p in n:
        if (p.tag == '{rok}FioHist'):
            import_fiohist(r, p, cnt, err)
        elif (p.tag == '{rok}Child'):
            import_child(r, p, cnt, err)
        elif (p.tag == '{rok}Appoint'):
            import_appoint(r, p, cnt, err)
        elif (p.tag == '{rok}Education'):
            import_education(r, p, cnt, err)
        elif (p.tag == '{rok}PersPer'):
            import_persper(r, p, cnt, err)
        else:
            err.append('[x] unexpected tag [import_person]:' + p.tag.__str__())

def import_periods(n, cnt, err):
    for p in n:
        if (p.tag != '{rok}Period'):
            err.append('[x] unexpected tag [import_periods]:' + p.tag.__str__())
        else:
            import_period(p, cnt, err)

def import_departs(n, cnt, err):
    for p in n:
        if (p.tag == '{rok}Depart'):
            import_depart(p, cnt, err)
        elif (p.tag == '{rok}DepHist'):
            import_dephist(p, cnt, err)
        elif (p.tag == '{rok}Post'):
            import_post(p, cnt, err)
        else:
            err.append('[x] unexpected tag [import_departs]:' + p.tag.__str__())

def import_persons(n, cnt, err):
    for p in n:
        if (p.tag == '{rok}Person'):
            import_person(p, cnt, err)
        else:
            err.append('[x] unexpected tag [import_persons]:' + p.tag.__str__())

def import_top(n, cnt, err):

    if (n.tag == '{rok}Periods'):
        import_periods(n, cnt, err)
        return

    if (n.tag == '{rok}Departs'):
        import_departs(n, cnt, err)
        return

    if (n.tag == '{rok}Persons'):
        import_persons(n, cnt, err)
        return

    err.append('[x] unexpected tag [import_top]:' + n.tag.__str__())

def import_all(cnt, err):
    err.clear()
    root = ET.parse('D:\\Python\\xml\\wage.xml').getroot()
    Period.objects.all().delete()
    Depart.objects.all().delete()
    DepHist.objects.all().delete()
    Post.objects.all().delete()
    Person.objects.all().delete()
    FioHist.objects.all().delete()
    Child.objects.all().delete()
    Appoint.objects.all().delete()
    Education.objects.all().delete()
    PersPer.objects.all().delete()
    #PayTitle.objects.all().delete()
    Payment.objects.all().delete()
    for n in root:
        import_top(n, cnt, err)
    #for t in PayTitle.objects.all():
    #    err.append('id: ' + str(t.id) + ', name: ' + t.name)
