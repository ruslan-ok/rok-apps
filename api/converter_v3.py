from collections import Counter
from todo.models import Grp, Lst, Task as OldTask, Step as OldStep
from note.models import Note
from task.models import Task, Step, Group, TaskGroup, Urls
from apart.models import Apart, Meter, Bill, Service, Price
from store.models import Entry
from proj.models import Projects, Expenses
from task.const import *
from todo.get_info import get_info as todo_get_info
from note.get_info import get_info as note_get_info
from news.get_info import get_info as news_get_info
from apart.views.apart import get_info as apart_get_info
from apart.views.meter import get_info as meter_get_info
from apart.views.serv import get_info as serv_get_info
from apart.views.price import get_info as price_get_info
from apart.views.bill import get_info as bill_get_info
from store.get_info import get_info as store_get_info
from expen.views import get_info as expen_get_info

STAGES = {
    'groups': 0,
    'todo': 0,
    'note_news': 0,
    'apart': 0,
    'store': 0,
    'expen': 1,
    'trip': 0,
    'fuel': 0,
    'work': 0,
    'health': 0,
    'docs': 0,
    'warr': 0,
    'photo': 0,
}

def convert_v3():
    counter = Counter()
    init(counter)
    convert(counter)
    done(counter)
    return dict(counter)


GRP_APP = 0
NUM_ROLE = 1
STR_ROLE = 2

STAGE_ROLES = {
    'expen': (APP_EXPEN, NUM_ROLE_EXPENSE, ROLE_EXPENSE),
}

def init(counter):
    for stage in STAGES:
        if STAGES[stage]:
            counter['del_TaskGroup_'+stage] += TaskGroup.objects.filter(role=STAGE_ROLES[stage][STR_ROLE]).delete()[0]
            if (stage == 'groups'):
                pass
            elif (stage == 'todo'):
                pass
            elif (stage == 'note_news'):
                pass
            elif (stage == 'apart'):
                pass
            elif (stage == 'store'):
                pass
            elif (stage == 'expen'):
                counter['upd_Task_'     +stage] += Task.objects.exclude(app_expen=NONE).update(app_expen=NONE)
            elif (stage == 'trip'):
                pass
            elif (stage == 'fuel'):
                pass
            elif (stage == 'work'):
                pass
            elif (stage == 'health'):
                pass
            elif (stage == 'docs'):
                pass
            elif (stage == 'warr'):
                pass
            elif (stage == 'photo'):
                pass
            counter['del_Task'] += Task.objects.filter(app_task=NONE, app_note=NONE, app_news=NONE, 
                        app_store=NONE, app_doc=NONE, app_warr=NONE, app_expen=NONE, app_trip=NONE, 
                        app_fuel=NONE, app_apart=NONE, app_health=NONE, app_work=NONE, app_photo=NONE).delete()[0]
            counter['del_Group_'+stage] += Group.objects.filter(app=STAGE_ROLES[stage][GRP_APP]).delete()[0]

def convert(counter):
    for stage in STAGES:
        if STAGES[stage]:
            if (stage == 'groups'):
                transfer_grp(None, None)
                transfer_lst(None, None)
            elif (stage == 'todo'):
                transfer_task(None, None)
            elif (stage == 'note_news'):
                transfer_note(None, None)
            elif (stage == 'apart'):
                transfer_apart()
                transfer_meter()
                transfer_service()
                transfer_price()
                transfer_bill()
            elif (stage == 'store'):
                transfer_store(None, None)
            elif (stage == 'expen'):
                transfer_expen_proj(stage, counter)
                transfer_expenses(stage, counter)
            elif (stage == 'trip'):
                transfer_pass()
            elif (stage == 'fuel'):
                transfer_pass()
            elif (stage == 'work'):
                transfer_pass()
            elif (stage == 'health'):
                transfer_pass()
            elif (stage == 'docs'):
                transfer_pass()
            elif (stage == 'warr'):
                transfer_pass()
            elif (stage == 'photo'):
                transfer_pass()

"""
    debug = []
    debug.append('Start convert')
    Task.objects.exclude(app_store=NONE).delete()
    task_len_before = len(Task.objects.all())
    urls_len_before = len(Urls.objects.all())
    TaskGroup.objects.all().delete()
    Group.objects.all().delete()
    Task.objects.all().delete()
    Step.objects.all().delete()
    Urls.objects.all().delete()
    transfer_grp(None, None, debug)
    transfer_lst(None, None, debug)
    transfer_task(None, None)
    transfer_note(None, None)
    transfer_apart()
    transfer_meter()
    transfer_service()
    transfer_price()
    transfer_bill()
    transfer_store(None, None)
    debug.append('Records in Grp: ' + str(len(Grp.objects.all())))
    debug.append('Records in Lst: ' + str(len(Lst.objects.all())))
    debug.append('Records in Group: ' + str(len(Group.objects.all())))
    debug.append('-')
    task_qty = len(OldTask.objects.all())
    note_qty = len(Note.objects.all())
    apart_qty = len(Apart.objects.all())
    serv_qty = len(Service.objects.all())
    meter_qty = len(Meter.objects.all())
    price_qty = len(Price.objects.all())
    bill_qty = len(Bill.objects.all())
    debug.append('Records in OldTask: ' + str(task_qty))
    debug.append('Records in Note: ' + str(note_qty))
    debug.append('Records in Apart: ' + str(apart_qty))
    debug.append('Records in Service: ' + str(serv_qty))
    debug.append('Records in Meter: ' + str(meter_qty))
    debug.append('Records in Price: ' + str(price_qty))
    debug.append('Records in Bill: ' + str(bill_qty))
    debug.append('Total: ' + str(task_qty + note_qty + apart_qty + serv_qty + meter_qty + bill_qty))
    debug.append('Total: ' + str(apart_qty + serv_qty + meter_qty + bill_qty + price_qty))
    debug.append('Records in Task added: ' + str(len(Task.objects.all())-task_len_before))
    debug.append('-')
    debug.append('Records in OldStep: ' + str(len(OldStep.objects.all())))
    debug.append('Records in Step: ' + str(len(Step.objects.all())))
    debug.append('-')
    debug.append('Records in Urls added: ' + str(len(Urls.objects.all())-urls_len_before))
    debug.append('Stop convert')
    return debug
"""

def done(counter):
    print(counter)

def transfer_pass():
    pass

def transfer_grp(grp_node, task_grp_node, debug):
    grps = Grp.objects.filter(node=grp_node)
    for grp in grps:
        """
        task_grp_node_id = None
        if task_grp_node:
            task_grp_node_id = task_grp_node.id
        if Group.objects.filter(user=grp.user.id, app=grp.app, role=grp.app, node=task_grp_node_id, name=grp.name, sort=grp.sort, created=grp.created, last_mod=grp.last_mod).exists():
            task_grp = Group.objects.filter(user=grp.user.id, app=grp.app, role=grp.app, node=task_grp_node_id, name=grp.name, sort=grp.sort, created=grp.created, last_mod=grp.last_mod).get()
        else:
            task_grp = Group.objects.create(user=grp.user, app=grp.app, role=grp.app, node=task_grp_node, name=grp.name, sort=grp.sort, created=grp.created, last_mod=grp.last_mod)
        """
        task_grp = Group.objects.create(user=grp.user, app=grp.app, role=grp.app, node=task_grp_node, name=grp.name, sort=grp.sort, created=grp.created, last_mod=grp.last_mod)
        transfer_grp(grp, task_grp, debug)
        transfer_lst(grp, task_grp, debug)


def transfer_lst(grp, task_grp, debug):
    lsts = Lst.objects.filter(grp=grp)
    """
    task_grp_id = None
    if task_grp:
        task_grp_id = task_grp.id
    """
    for lst in lsts:
        """
        if Group.objects.filter(user=lst.user.id, app=lst.app, role=lst.app, node=task_grp_id, name=lst.name, sort=lst.sort, created=lst.created, last_mod=lst.last_mod).exists():
            task_grp_ = Group.objects.filter(user=lst.user.id, app=lst.app, role=lst.app, node=task_grp_id, name=lst.name, sort=lst.sort, created=lst.created, last_mod=lst.last_mod).get()
        else:
            task_grp_ = Group.objects.create(user=lst.user, app=lst.app, role=lst.app, node=task_grp, name=lst.name, sort=lst.sort, created=lst.created, last_mod=lst.last_mod)
        """
        task_grp_ = Group.objects.create(user=lst.user, app=lst.app, role=lst.app, node=task_grp, name=lst.name, sort=lst.sort, created=lst.created, last_mod=lst.last_mod)
        transfer_task(lst, task_grp_)
        transfer_note(lst, task_grp_)
        transfer_store(lst, task_grp_)


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

        atask.set_item_attr(APP_TODO, todo_get_info(atask))

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
                                    app_note=note_role,
                                    app_news=news_role,
                                    created=note.publ,
                                    last_mod=note.last_mod)
        
        if task_grp:
            TaskGroup.objects.create(task=atask, group=task_grp, role=task_grp.role)

        if note.url:
            Urls.objects.create(task=atask, num=1, href=note.url)

        if note.kind == 'note':
            atask.set_item_attr(APP_NOTE, note_get_info(atask))
        else:
            atask.set_item_attr(APP_NEWS, news_get_info(atask))

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
        atask.set_item_attr(APP_APART, apart_get_info(atask))

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
        atask.set_item_attr(APP_APART, meter_get_info(atask))

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
        atask.set_item_attr(APP_APART, serv_get_info(atask))

def transfer_price():
    prices = Price.objects.all()
    for price in prices:
        atask = Task.objects.create(user=price.apart.user,
                                    start=price.start,
                                    name=price.start.strftime('%Y.%m.%d') + ' ' + price.serv.name,
                                    info=price.info,
                                    app_apart=NUM_ROLE_PRICE,
                                    )
        price.task = atask
        price.save()
        atask.set_item_attr(APP_APART, price_get_info(atask))

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

        atask.set_item_attr(APP_APART, bill_get_info(atask))

def transfer_store(lst, task_grp):
    items = Entry.objects.filter(lst=lst)
    for item in items:
        atask = Task.objects.create(user=item.user,
                                    name=item.title,
                                    categories=item.categories,
                                    info=item.notes if item.notes else '',
                                    app_store=NUM_ROLE_STORE)
        
        if task_grp:
            TaskGroup.objects.create(task=atask, group=task_grp, role=task_grp.role)

        if item.url:
            Urls.objects.create(task=atask, num=1, href=item.url)

        atask.set_item_attr(APP_STORE, store_get_info(atask))

def transfer_expen_proj(stage, counter):
    items = Projects.objects.all()
    for item in items:
        Group.objects.create(user=item.user,
                            app=STAGE_ROLES[stage][GRP_APP],
                            role=STAGE_ROLES[stage][STR_ROLE],
                            node=None,
                            name=item.name,
                            sort=str(item.id),
                            created=item.created,
                            last_mod=item.last_mod,
                            tot_byn=item.tot_byn,
                            tot_usd=item.tot_usd,
                            tot_eur=item.tot_eur,
                            )
        counter['add_Group_'+stage] += 1

def transfer_expenses(stage, counter):
    items = Expenses.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.direct.user,
                                    app_expen=STAGE_ROLES[stage][NUM_ROLE],
                                    event=item.date,
                                    name = item.description,
                                    created=item.created,
                                    last_mod=item.last_mod,
                                    info=item.text,
                                    qty=item.qty,
                                    price=item.price,
                                    rate=item.rate,
                                    rate_2=item.rate_2,
                                    usd=item.usd,
                                    eur=item.eur,
                                    kontr=item.kontr,
                                    )
        counter['add_Task_'+stage] += 1

        if Group.objects.filter(user=atask.user_id, app=APP_EXPEN, sort=str(item.direct.id)).exists():
            task_grp = Group.objects.filter(user=atask.user_id, app=APP_EXPEN, sort=str(item.direct.id)).get()
            TaskGroup.objects.create(task=atask, group=task_grp, role=STAGE_ROLES[stage][STR_ROLE])
            counter['add_TaskGroup_'+stage] += 1

        atask.set_item_attr(APP_EXPEN, expen_get_info(atask))
