from todo.models import Grp, Lst, Task
from note.models import Note
from task.models import TaskGrp, ATask, TaskUrls
from task.const import *

debug = []


def convert():
    debug = []
    debug.append('Start convert')
    TaskGrp.objects.all().delete()
    ATask.objects.all().delete()
    TaskUrls.objects.all().delete()
    transfer_grp(None, None, debug)
    transfer_lst(None, None, debug)
    transfer_task(None, None)
    transfer_note(None, None)
    debug.append('Records in Grp: ' + str(len(Grp.objects.all())))
    debug.append('Records in Lst: ' + str(len(Lst.objects.all())))
    debug.append('Records in TaskGrp: ' + str(len(TaskGrp.objects.all())))
    debug.append('-')
    task_qty = len(Task.objects.all())
    note_qty = len(Note.objects.all())
    debug.append('Records in Task: ' + str(task_qty))
    debug.append('Records in Note: ' + str(note_qty))
    debug.append('Total: ' + str(task_qty + note_qty))
    debug.append('Records in ATask: ' + str(len(ATask.objects.all())))
    debug.append('-')
    debug.append('Records in TaskUrls: ' + str(len(TaskUrls.objects.all())))
    debug.append('Stop convert')
    return debug


def transfer_grp(grp_node, task_grp_node, debug):
    grps = Grp.objects.filter(node=grp_node)
    for grp in grps:
        is_leaf = not Lst.objects.filter(grp=grp).exists()
        task_grp = TaskGrp.objects.create(user=grp.user, app=grp.app, node=task_grp_node, name=grp.name, sort=grp.sort, is_open=grp.is_open, created=grp.created, last_mod=grp.last_mod, is_leaf=is_leaf)
        transfer_grp(grp, task_grp, debug)
        transfer_lst(grp, task_grp, debug)


def transfer_lst(grp, task_grp, debug):
    lsts = Lst.objects.filter(grp=grp)
    for lst in lsts:
        task_grp_ = TaskGrp.objects.create(user=lst.user, app=lst.app, node=task_grp, name=lst.name, sort=lst.sort, created=lst.created, last_mod=lst.last_mod, is_leaf=True)
        transfer_task(lst, task_grp_)
        transfer_note(lst, task_grp_)


def transfer_task(lst, task_grp):
    tasks = Task.objects.filter(lst=lst)
    for task in tasks:
        atask = ATask.objects.create(user=task.user,
                             grp=task_grp,
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
                             app_task=TASK,
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
        if task.url:
            TaskUrls.objects.create(task=atask, num=1, href=task.url)


def transfer_note(lst, task_grp):
    notes = Note.objects.filter(lst=lst)
    for note in notes:
        note_role = NONE
        news_role = NONE
        if note.kind == 'note':
            note_role = NOTE
        else:
            news_role = NEWS
        atask = ATask.objects.create(user=note.user,
                             grp=task_grp,
                             name=note.name,
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
        if note.url:
            TaskUrls.objects.create(task=atask, num=1, href=note.url)
