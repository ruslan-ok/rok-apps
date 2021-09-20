from todo.models import Grp, Lst, Task as OldTask, Step as OldStep
from note.models import Note
from task.models import Task, Step, Group, TaskGroup, Urls
from task.const import *

debug = []


def convert_v3():
    debug = []
    debug.append('Start convert')
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
    debug.append('Records in Grp: ' + str(len(Grp.objects.all())))
    debug.append('Records in Lst: ' + str(len(Lst.objects.all())))
    debug.append('Records in Group: ' + str(len(Group.objects.all())))
    debug.append('-')
    task_qty = len(OldTask.objects.all())
    note_qty = len(Note.objects.all())
    debug.append('Records in OldTask: ' + str(task_qty))
    debug.append('Records in Note: ' + str(note_qty))
    debug.append('Total: ' + str(task_qty + note_qty))
    debug.append('Records in Task: ' + str(len(Task.objects.all())))
    debug.append('-')
    debug.append('Records in OldStep: ' + str(len(OldStep.objects.all())))
    debug.append('Records in Step: ' + str(len(Step.objects.all())))
    debug.append('-')
    debug.append('Records in Urls: ' + str(len(Urls.objects.all())))
    debug.append('Stop convert')
    return debug


def transfer_grp(grp_node, task_grp_node, debug):
    grps = Grp.objects.filter(node=grp_node)
    for grp in grps:
        task_grp = Group.objects.create(user=grp.user, role=grp.app, node=task_grp_node, name=grp.name, sort=grp.sort, created=grp.created, last_mod=grp.last_mod)
        transfer_grp(grp, task_grp, debug)
        transfer_lst(grp, task_grp, debug)


def transfer_lst(grp, task_grp, debug):
    lsts = Lst.objects.filter(grp=grp)
    for lst in lsts:
        task_grp_ = Group.objects.create(user=lst.user, role=lst.app, node=task_grp, name=lst.name, sort=lst.sort, created=lst.created, last_mod=lst.last_mod)
        transfer_task(lst, task_grp_)
        transfer_note(lst, task_grp_)


def transfer_task(lst, task_grp):
    tasks = OldTask.objects.filter(lst=lst)
    for task in tasks:
        atask = Task.objects.create(user=task.user,
                                    name=task.name,
                                    event=None,
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
                                    app_note=NONE,
                                    app_news=NONE,
                                    app_store=NONE,
                                    app_doc=NONE,
                                    app_warr=NONE,
                                    app_expen=NONE,
                                    app_trip=NONE,
                                    app_fuel=NONE,
                                    app_apart=NONE,
                                    app_health=NONE,
                                    app_work=NONE,
                                    app_photo=NONE,
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
                                    start=None,
                                    stop=None,
                                    completed=False,
                                    completion=None,
                                    in_my_day=False,
                                    important=False,
                                    remind=None,
                                    last_remind=None,
                                    repeat=0,
                                    repeat_num=0,
                                    repeat_days=0,
                                    categories=note.categories,
                                    info=note.descr,
                                    app_task=NONE,
                                    app_note=note_role,
                                    app_news=news_role,
                                    app_store=NONE,
                                    app_doc=NONE,
                                    app_warr=NONE,
                                    app_expen=NONE,
                                    app_trip=NONE,
                                    app_fuel=NONE,
                                    app_apart=NONE,
                                    app_health=NONE,
                                    app_work=NONE,
                                    app_photo=NONE,
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
        if apart.has_gas:
            param += 1
        if apart.has_ppo:
            param += 2
        atask = Task.objects.create(user=apart.user,
                                    name=apart.name,
                                    event=None,
                                    start=None,
                                    stop=None,
                                    completed=False,
                                    completion=None,
                                    in_my_day=False,
                                    important=apart.active,
                                    remind=None,
                                    last_remind=None,
                                    repeat=param,
                                    repeat_num=0,
                                    repeat_days=0,
                                    categories='',
                                    info=apart.addr,
                                    app_task=NONE,
                                    app_note=NONE,
                                    app_news=NONE,
                                    app_store=NONE,
                                    app_doc=NONE,
                                    app_warr=NONE,
                                    app_expen=NONE,
                                    app_trip=NONE,
                                    app_fuel=NONE,
                                    app_apart=NUM_ROLE_APART,
                                    app_health=NONE,
                                    app_work=NONE,
                                    app_photo=NONE
                                    )

