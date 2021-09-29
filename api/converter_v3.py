from todo.models import Grp, Lst, Task as OldTask, Step as OldStep
from note.models import Note
from task.models import Task, Step, Group, TaskGroup, Urls
from apart.models import Apart, Meter, Bill, Service, Price
from task.const import *

debug = []


def convert_v3():
    debug = []
    debug.append('Start convert')
    Task.objects.exclude(app_apart=NONE).delete()
    task_len_before = len(Task.objects.all())
    urls_len_before = len(Urls.objects.all())
    #TaskGroup.objects.all().delete()
    #Group.objects.all().delete()
    #Task.objects.all().delete()
    #Step.objects.all().delete()
    #Urls.objects.all().delete()
    #transfer_grp(None, None, debug)
    #transfer_lst(None, None, debug)
    #transfer_task(None, None)
    #transfer_note(None, None)
    transfer_apart()
    transfer_meter()
    transfer_service()
    transfer_price()
    transfer_bill()
    #debug.append('Records in Grp: ' + str(len(Grp.objects.all())))
    #debug.append('Records in Lst: ' + str(len(Lst.objects.all())))
    #debug.append('Records in Group: ' + str(len(Group.objects.all())))
    #debug.append('-')
    #task_qty = len(OldTask.objects.all())
    #note_qty = len(Note.objects.all())
    apart_qty = len(Apart.objects.all())
    serv_qty = len(Service.objects.all())
    meter_qty = len(Meter.objects.all())
    price_qty = len(Price.objects.all())
    bill_qty = len(Bill.objects.all())
    #debug.append('Records in OldTask: ' + str(task_qty))
    #debug.append('Records in Note: ' + str(note_qty))
    debug.append('Records in Apart: ' + str(apart_qty))
    debug.append('Records in Service: ' + str(serv_qty))
    debug.append('Records in Meter: ' + str(meter_qty))
    debug.append('Records in Price: ' + str(price_qty))
    debug.append('Records in Bill: ' + str(bill_qty))
    #debug.append('Total: ' + str(task_qty + note_qty + apart_qty + serv_qty + meter_qty + bill_qty))
    debug.append('Total: ' + str(apart_qty + serv_qty + meter_qty + bill_qty + price_qty))
    debug.append('Records in Task added: ' + str(len(Task.objects.all())-task_len_before))
    debug.append('-')
    #debug.append('Records in OldStep: ' + str(len(OldStep.objects.all())))
    #debug.append('Records in Step: ' + str(len(Step.objects.all())))
    debug.append('-')
    debug.append('Records in Urls added: ' + str(len(Urls.objects.all())-urls_len_before))
    debug.append('Stop convert')
    return debug


def transfer_grp(grp_node, task_grp_node, debug):
    grps = Grp.objects.filter(node=grp_node)
    for grp in grps:
        task_grp = Group.objects.create(user=grp.user, app=grp.app, role=grp.app, node=task_grp_node, name=grp.name, sort=grp.sort, created=grp.created, last_mod=grp.last_mod)
        transfer_grp(grp, task_grp, debug)
        transfer_lst(grp, task_grp, debug)


def transfer_lst(grp, task_grp, debug):
    lsts = Lst.objects.filter(grp=grp)
    for lst in lsts:
        task_grp_ = Group.objects.create(user=lst.user, app=lst.app, role=lst.app, node=task_grp, name=lst.name, sort=lst.sort, created=lst.created, last_mod=lst.last_mod)
        transfer_task(lst, task_grp_)
        transfer_note(lst, task_grp_)


def transfer_task(lst, task_grp):
    tasks = OldTask.objects.filter(lst=lst)
    for task in tasks:
        atask = Task.objects.create(user=task.user,
                                    name=task.name,
                                    start=task.start,
                                    stop=task.stop,
                                    completed=task.completed,
                                    completion=task.completion,
                                    in_my_day=task.in_my_day,
                                    important=task.important,
                                    remind=task.remind,
                                    last_remind=task.last_remind,
                                    repeat=task.repeat,
                                    repeat_num=task.repeat_num,
                                    repeat_days=task.repeat_days,
                                    categories=task.categories,
                                    info=task.info,
                                    app_task=NUM_ROLE_TODO,
                                    created=task.created,
                                    last_mod=task.last_mod)
        
        for step in OldStep.objects.filter(task=task.id):
            Step.objects.create(user=step.task.user, task=atask, name=step.name, sort=step.sort, completed=step.completed)
        
        if task_grp:
            TaskGroup.objects.create(task=atask, group=task_grp, role=task_grp.role)
        
        if task.url:
            Urls.objects.create(task=atask, num=1, href=task.url)

def transfer_note(lst, task_grp):
    notes = Note.objects.filter(lst=lst)
    for note in notes:
        note_role = NONE
        news_role = NONE
        if note.kind == 'note':
            note_role = NUM_ROLE_NOTE
        else:
            news_role = NUM_ROLE_NEWS
        atask = Task.objects.create(user=note.user,
                                    name=note.name,
                                    event=note.publ,
                                    categories=note.categories,
                                    info=note.descr,
                                    app_task=NONE,
                                    app_note=note_role,
                                    app_news=news_role,
                                    created=note.publ,
                                    last_mod=note.last_mod)
        
        if task_grp:
            TaskGroup.objects.create(task=atask, group=task_grp, role=task_grp.role)

        if note.url:
            Urls.objects.create(task=atask, num=1, href=note.url)

def transfer_apart():
    aparts = Apart.objects.all()
    for apart in aparts:
        param = 0
        atask = Task.objects.create(user=apart.user,
                                    name=apart.name,
                                    important=apart.active,
                                    info=apart.addr,
                                    app_apart=NUM_ROLE_APART,
                                    )
        apart.task = atask
        apart.save()

def transfer_meter():
    meters = Meter.objects.all()
    for meter in meters:
        atask = Task.objects.create(user=meter.apart.user,
                                    event=meter.reading,
                                    name=meter.period.strftime('%Y.%m'),
                                    start=meter.period,
                                    info=meter.info,
                                    app_apart=NUM_ROLE_METER,
                                    )
        meter.task = atask
        meter.save()

def transfer_service():
    services = Service.objects.all()
    for serv in services:
        atask = Task.objects.create(user=serv.apart.user,
                                    name=serv.name,
                                    info=serv.abbr,
                                    app_apart=NUM_ROLE_SERVICE,
                                    )
        serv.task = atask
        serv.save()

def transfer_price():
    prices = Price.objects.all()
    for price in prices:
        atask = Task.objects.create(user=price.apart.user,
                                    start=price.start,
                                    name=price.start.strftime('%Y.%m.%d'),
                                    info=price.info,
                                    app_apart=NUM_ROLE_PRICE,
                                    )
        price.task = atask
        price.save()

def transfer_bill():
    bills = Bill.objects.all()
    for bill in bills:
        atask = Task.objects.create(user=bill.apart.user,
                                    event=bill.payment,
                                    name=bill.period.strftime('%Y.%m'),
                                    start=bill.period,
                                    info=bill.info,
                                    app_apart=NUM_ROLE_BILL,
                                    )
        bill.task = atask
        bill.save()

        if bill.url:
            Urls.objects.create(task=atask, num=1, href=bill.url)
