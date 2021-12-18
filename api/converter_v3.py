from datetime import datetime
from todo.models import Grp, Lst, Task as OldTask, Step as OldStep
from note.models import Note
from task.models import Task, Step, Group, TaskGroup, Urls
from apart.models import Apart, Meter, Bill, Service, Price
from store.models import Entry
from proj.models import Projects, Expenses
from fuel.models import Car, Fuel, Part, Repl
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
from fuel.views.fuel import get_info as fuel_get_info
from fuel.views.serv import get_info as repl_get_info
from fuel.views.part import get_info as part_get_info

STAGES = {
    APP_TODO: 0,
    APP_NOTE: 0,
    APP_NEWS: 0,
    APP_STORE: 1,
    APP_EXPEN: 0,
    APP_TRIP: 0,
    APP_FUEL: 0,
    APP_APART: 0,
    APP_WORK: 0,
    APP_HEALTH: 0,
    APP_DOCS: 0,
    APP_WARR: 0,
    APP_PHOTO: 0,
}

def convert_v3():
    result = {}
    result['start'] = datetime.now()
    init(result)
    convert(result)
    result['stop'] = datetime.now()
    done(result)
    return result

def set(result, app, role, table, oper, qnt: int):
    if (qnt == 0) and (table not in result[app][role]):
        return
    if (qnt == 0) and (oper not in result[app][role][table]):
        return
    if (table not in result[app][role]):
        result[app][role][table] = {}
    result[app][role][table][oper] = qnt

def inc(result, app, role, table, oper):
    if (table not in result[app][role]):
        result[app][role][table] = {}
    if (oper not in result[app][role][table]):
        result[app][role][table][oper] = 1
    else:
        result[app][role][table][oper] += 1

def get_excluded(app, kind):
    if (app != APP_TODO):
        return []
    leave_groups = Group.objects.filter(name__contains='Сайт 3.0')
    if (kind == 'Group'):
        return leave_groups
    leave_tgs = TaskGroup.objects.filter(role=ROLE_TODO).filter(group__in=leave_groups)
    if (kind == 'TaskGroup'):
        return leave_tgs
    return leave_tgs.values('task')

def delete_task_role(app, role, result):
    data = Task.get_role_tasks(None, app, role).exclude(id__in=get_excluded(app, 'Task'))
    if (app == APP_TODO):
        qnt = data.update(app_task=NONE)
    if (app == APP_NOTE):
        qnt = data.update(app_note=NONE)
    if (app == APP_NEWS):
        qnt = data.update(app_news=NONE)
    if (app == APP_STORE):
        qnt = data.update(app_store=NONE)
    if (app == APP_DOCS):
        qnt = data.update(app_doc=NONE)
    if (app == APP_WARR):
        qnt = data.update(app_warr=NONE)
    if (app == APP_EXPEN):
        qnt = data.update(app_expen=NONE)
    if (app == APP_TRIP):
        qnt = data.update(app_trip=NONE)
    if (app == APP_FUEL):
        qnt = data.update(app_fuel=NONE)
    if (app == APP_APART):
        qnt = data.update(app_apart=NONE)
    if (app == APP_HEALTH):
        qnt = data.update(app_health=NONE)
    if (app == APP_WORK):
        qnt = data.update(app_work=NONE)
    if (app == APP_PHOTO):
        qnt = data.update(app_photo=NONE)
    set(result, app, role, 'Task', 'reset_role', qnt)
    to_kill = Task.objects.filter(app_task=NONE, app_note=NONE, app_news=NONE, 
                        app_store=NONE, app_doc=NONE, app_warr=NONE, app_expen=NONE, app_trip=NONE, 
                        app_fuel=NONE, app_apart=NONE, app_health=NONE, app_work=NONE, app_photo=NONE)
    set(result, app, role, 'Step', 'delete', Step.objects.filter(task__in=to_kill).delete()[0])
    set(result, app, role, 'Urls', 'delete', Urls.objects.filter(task__in=to_kill).delete()[0])
    set(result, app, role, 'Task', 'delete', to_kill.delete()[0])

def init(result):
    for app in STAGES:
        if STAGES[app]:
            result[app] = {}
            for role in ROLES_IDS[app]:
                result[app][role] = {}
                delete_task_role(app, role, result)
                set(result, app, role, 'TaskGroup', 'delete', TaskGroup.objects.filter(role=role).exclude(id__in=get_excluded(app, 'TaskGroup')).delete()[0])
                set(result, app, role, 'Group', 'delete', Group.objects.filter(app=app).exclude(id__in=get_excluded(app, 'Group')).delete()[0])

def convert(result):
    for app in STAGES:
        if STAGES[app]:
            for role in ROLES_IDS[app]:
                transfer_grp(result, app, role, None, None)
                transfer_lst(result, app, role, None, None)
            if (app == APP_TODO):
                transfer_task(result, None, None)
            if (app == APP_NOTE):
                transfer_note(result, app, role, None, None)
            if (app == APP_NEWS):
                transfer_note(result, app, role, None, None)
            if (app == APP_STORE):
                transfer_store(result, None, None)
            if (app == APP_DOCS):
                pass
            if (app == APP_WARR):
                pass
            if (app == APP_EXPEN):
                transfer_expen_proj(result)
                transfer_expenses(result)
            if (app == APP_TRIP):
                pass
            if (app == APP_FUEL):
                transfer_car(result)
                transfer_fuel(result)
                transfer_part(result)
                transfer_repl(result)
            if (app == APP_APART):
                transfer_apart(result)
                transfer_meter(result)
                transfer_service(result)
                transfer_price(result)
                transfer_bill(result)
            if (app == APP_HEALTH):
                pass
            if (app == APP_WORK):
                pass
            if (app == APP_PHOTO):
                pass

def done(result):
    print(result)

def transfer_grp(result, app, role, grp_node, task_grp_node):
    grps = Grp.objects.filter(app=app, node=grp_node)
    for grp in grps:
        task_grp = Group.objects.create(user=grp.user, app=grp.app, role=grp.app, node=task_grp_node, name=grp.name, sort=grp.sort, created=grp.created, last_mod=grp.last_mod)
        inc(result, app, role, 'Group', 'added')
        transfer_grp(result, app, role, grp, task_grp)
        transfer_lst(result, app, role, grp, task_grp)

def transfer_lst(result, app, role, grp, task_grp):
    lsts = Lst.objects.filter(app=app, grp=grp)
    for lst in lsts:
        task_grp_ = Group.objects.create(user=lst.user, app=lst.app, role=lst.app, node=task_grp, name=lst.name, sort=lst.sort, created=lst.created, last_mod=lst.last_mod)
        inc(result, app, role, 'Group', 'added')
        if (role == ROLE_TODO):
            transfer_task(result, lst, task_grp_)
        if (role == ROLE_NOTE) or (role == ROLE_NEWS):
            transfer_note(result, app, role, lst, task_grp_)
        if (role == ROLE_STORE):
            transfer_store(result, lst, task_grp_)

def transfer_task(result, lst, task_grp):
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
        inc(result, APP_TODO, ROLE_TODO, 'Task', 'added')
        
        for step in OldStep.objects.filter(task=task.id):
            Step.objects.create(user=step.task.user, task=atask, name=step.name, sort=step.sort, completed=step.completed)
            inc(result, APP_TODO, ROLE_TODO, 'Step', 'added')
        
        if task_grp:
            TaskGroup.objects.create(task=atask, group=task_grp, role=task_grp.role)
            inc(result, APP_TODO, ROLE_TODO, 'TaskGroup', 'added')
        
        if task.url:
            Urls.objects.create(task=atask, num=1, href=task.url)
            inc(result, APP_TODO, ROLE_TODO, 'Urls', 'added')

        atask.set_item_attr(APP_TODO, todo_get_info(atask))

def transfer_note(result, app, role, lst, task_grp):
    notes = Note.objects.filter(lst=lst)
    for note in notes:
        if (note.kind == 'note') and (role != ROLE_NOTE):
            continue
        if (note.kind == 'news') and (role != ROLE_NEWS):
            continue
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
        inc(result, app, role, 'Task', 'added')
        
        if task_grp:
            TaskGroup.objects.create(task=atask, group=task_grp, role=task_grp.role)
            inc(result, app, role, 'TaskGroup', 'added')

        if note.url:
            Urls.objects.create(task=atask, num=1, href=note.url)
            inc(result, app, role, 'Urls', 'added')

        if note.kind == 'note':
            atask.set_item_attr(APP_NOTE, note_get_info(atask))
        else:
            atask.set_item_attr(APP_NEWS, news_get_info(atask))

def transfer_apart(result):
    items = Apart.objects.all()
    for item in items:
        Group.objects.create(user=item.user,
                            app=APP_APART,
                            role=ROLE_APART,
                            node=None,
                            name=item.name,
                            sort=str(item.id),
                            info=item.addr,
                            has_el=item.has_el,
                            has_hw=item.has_hw,
                            has_cw=item.has_cw,
                            has_gas=item.has_gas,
                            has_ppo=item.has_ppo,
                            has_tv=item.has_tv,
                            has_phone=item.has_phone,
                            has_zkx=item.has_zkx,
                            )
        inc(result, APP_APART, ROLE_APART, 'Group', 'added')

def transfer_meter(result):
    items = Meter.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.apart.user,
                                    event=item.reading,
                                    name=item.period.strftime('%Y.%m'),
                                    start=item.period,
                                    info=item.info,
                                    app_apart=NUM_ROLE_METER,
                                    )
        inc(result, APP_APART, ROLE_METER, 'Task', 'added')
        item.task = atask
        item.save()
        link_group(result, atask.user_id, APP_APART, ROLE_METER, str(item.apart.id), atask)
        atask.set_item_attr(APP_APART, meter_get_info(atask))

def transfer_service(result):
    items = Service.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.apart.user,
                                    name=item.name,
                                    info=item.abbr,
                                    app_apart=NUM_ROLE_SERVICE,
                                    )
        inc(result, APP_APART, ROLE_SERVICE, 'Task', 'added')
        item.task = atask
        item.save()
        link_group(result, atask.user_id, APP_APART, ROLE_SERVICE, str(item.apart.id), atask)
        atask.set_item_attr(APP_APART, serv_get_info(atask))

def transfer_price(result):
    items = Price.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.apart.user,
                                    start=item.start,
                                    name=item.start.strftime('%Y.%m.%d') + ' ' + item.serv.name,
                                    info=item.info,
                                    app_apart=NUM_ROLE_PRICE,
                                    )
        inc(result, APP_APART, ROLE_PRICE, 'Task', 'added')
        item.task = atask
        item.save()
        link_group(result, atask.user_id, APP_APART, ROLE_PRICE, str(item.apart.id), atask)
        atask.set_item_attr(APP_APART, price_get_info(atask))

def transfer_bill(result):
    items = Bill.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.apart.user,
                                    event=item.payment,
                                    name=item.period.strftime('%Y.%m'),
                                    start=item.period,
                                    info=item.info,
                                    app_apart=NUM_ROLE_BILL,
                                    )
        inc(result, APP_APART, ROLE_BILL, 'Task', 'added')
        item.task = atask
        item.save()
        link_group(result, atask.user_id, APP_APART, ROLE_BILL, str(item.apart.id), atask)

        if item.url:
            Urls.objects.create(task=atask, num=1, href=item.url)
            inc(result, APP_APART, ROLE_BILL, 'Urls', 'added')

        atask.set_item_attr(APP_APART, bill_get_info(atask))

def transfer_store(result, lst, task_grp):
    items = Entry.objects.filter(lst=lst, actual=True)
    for item in items:
        atask = Task.objects.create(user=item.user,
                                    name=item.title,
                                    categories=item.categories,
                                    info=item.notes if item.notes else '',
                                    app_store=NUM_ROLE_STORE)
        inc(result, APP_STORE, ROLE_STORE, 'Task', 'added')
        item.task = atask
        item.save()
        
        if task_grp:
            TaskGroup.objects.create(task=atask, group=task_grp, role=task_grp.role)
            inc(result, APP_STORE, ROLE_STORE, 'TaskGroup', 'added')

        if item.url:
            Urls.objects.create(task=atask, num=1, href=item.url)
            inc(result, APP_STORE, ROLE_STORE, 'Urls', 'added')

        atask.set_item_attr(APP_STORE, store_get_info(atask))

    items = Entry.objects.filter(lst=lst, actual=False)
    for item in items:
        if task_grp:
            atasks = Task.objects.filter(user=item.user.id, name=item.title, app_store=NUM_ROLE_STORE, groups__id=task_grp.id)
        else:
            atasks = Task.objects.filter(user=item.user.id, name=item.title, app_store=NUM_ROLE_STORE, groups__id=None)

        if (len(atasks) > 1):
            print('oops')
            break

        if (len(atasks) == 1):
            atask = atasks[0]
            if item.url:
                Urls.objects.create(task=atask, num=2, href=item.url)
                inc(result, APP_STORE, ROLE_STORE, 'Urls', 'added')
            item.task = atask
            item.save()
        else:
            atask = Task.objects.create(user=item.user,
                                        name=item.title,
                                        categories=item.categories,
                                        info=item.notes if item.notes else '',
                                        app_store=NUM_ROLE_STORE)
            inc(result, APP_STORE, ROLE_STORE, 'Task', 'added_broken_Entry')
            item.task = atask
            item.save()
            
            if task_grp:
                TaskGroup.objects.create(task=atask, group=task_grp, role=task_grp.role)
                inc(result, APP_STORE, ROLE_STORE, 'TaskGroup', 'added')

            if item.url:
                Urls.objects.create(task=atask, num=1, href=item.url)
                inc(result, APP_STORE, ROLE_STORE, 'Urls', 'added')

            atask.set_item_attr(APP_STORE, store_get_info(atask))


def transfer_expen_proj(result):
    items = Projects.objects.all()
    for item in items:
        Group.objects.create(user=item.user,
                            app=APP_EXPEN,
                            role=ROLE_EXPENSE,
                            node=None,
                            name=item.name,
                            sort=str(item.id),
                            created=item.created,
                            last_mod=item.last_mod,
                            tot_byn=item.tot_byn,
                            tot_usd=item.tot_usd,
                            tot_eur=item.tot_eur,
                            )
        inc(result, APP_EXPEN, ROLE_EXPENSE, 'Group', 'added')

def transfer_expenses(result):
    items = Expenses.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.direct.user,
                                    app_expen=NUM_ROLE_EXPENSE,
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
        inc(result, APP_EXPEN, ROLE_EXPENSE, 'Task', 'added')
        link_group(result, atask.user_id, APP_EXPEN, ROLE_EXPENSE, str(item.direct.id), atask)
        atask.set_item_attr(APP_EXPEN, expen_get_info(atask))

def transfer_car(result):
    items = Car.objects.all()
    for item in items:
        Group.objects.create(user=item.user,
                            app=APP_FUEL,
                            role=ROLE_CAR,
                            node=None,
                            name=item.name,
                            sort=str(item.id),
                            info=item.plate,
                            )
        inc(result, APP_FUEL, ROLE_CAR, 'Group', 'added')

def transfer_fuel(result):
    items = Fuel.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.car.user,
                                    app_fuel=NUM_ROLE_FUEL,
                                    event=item.pub_date,
                                    name=str(item.odometer),
                                    qty=item.volume,
                                    price=item.price,
                                    info=item.comment,
                                    created=item.created,
                                    last_mod=item.last_mod,
                                    )
        inc(result, APP_FUEL, ROLE_FUEL, 'Task', 'added')
        link_group(result, atask.user_id, APP_FUEL, ROLE_FUEL, str(item.car.id), atask)
        atask.set_item_attr(APP_FUEL, fuel_get_info(atask))

def transfer_part(result):
    items = Part.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.car.user,
                                    app_fuel=NUM_ROLE_PART,
                                    event=item.pub_date,
                                    name=str(item.odometer),
                                    qty=item.volume,
                                    price=item.price,
                                    info=item.comment,
                                    created=item.created,
                                    last_mod=item.last_mod,
                                    )
        inc(result, APP_FUEL, ROLE_PART, 'Task', 'added')
        link_group(result, atask.user_id, APP_FUEL, ROLE_PART, str(item.car.id), atask)
        atask.set_item_attr(APP_FUEL, part_get_info(atask))

def transfer_repl(result):
    items = Repl.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.car.user,
                                    app_fuel=NUM_ROLE_SERVICE,
                                    event=item.pub_date,
                                    name=str(item.odometer),
                                    qty=item.volume,
                                    price=item.price,
                                    info=item.comment,
                                    created=item.created,
                                    last_mod=item.last_mod,
                                    )
        inc(result, APP_FUEL, ROLE_SERVICE, 'Task', 'added')
        link_group(result, atask.user_id, APP_FUEL, ROLE_SERVICE, str(item.car.id), atask)
        atask.set_item_attr(APP_FUEL, repl_get_info(atask))


def link_group(result, user_id, app, role, todo_grp_id, task):
        if Group.objects.filter(user=user_id, app=app, sort=todo_grp_id).exists():
            task_grp = Group.objects.filter(user=user_id, app=app, sort=todo_grp_id).get()
            TaskGroup.objects.create(task=task, group=task_grp, role=role)
            inc(result, app, role, 'TaskGroup', 'added')

