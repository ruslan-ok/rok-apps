import os.path, requests, json
from datetime import datetime

from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, permissions, renderers, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from task import const
from task.models import Task, Group, TaskGroup, GIQ_ADD_TASK, GIQ_DEL_TASK, CurrencyRate
from rusel.utils import nice_date
from api.serializers import TaskSerializer

from apart.views.meter import add_meter
from apart.views.price import add_price
from apart.views.bill import add_bill
from fuel.views.fuel import add_fuel
from fuel.views.part import add_part
from fuel.views.serv import add_serv
from health.views.marker import add_item as add_marker
from store.views import add_item as add_store

from note.get_info import get_info as note_get_info
from news.get_info import get_info as news_get_info
from store.get_info import get_info as store_get_info
from apart.views.apart import get_info as apart_get_info
from apart.views.price import get_info as price_get_info
from apart.views.meter import get_info as meter_get_info
from apart.views.bill import get_info as bill_get_info
from health.views.marker import get_info as marker_get_info
from health.views.incident import get_info as incident_get_info
from warr.views import get_info as warr_get_info
from expen.views import get_info as expen_get_info
from fuel.views.car import get_info as car_get_info
from fuel.views.fuel import get_info as fuel_get_info
from fuel.views.part import get_info as part_get_info
from fuel.views.serv import get_info as serv_get_info

from service.background_services import check_services

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        data = Task.objects.filter(user=self.request.user.id).order_by('-created')
        if 'app' in self.request.query_params and 'role' in self.request.query_params:
            app = self.request.query_params['app']
            role = self.request.query_params['role']
            return Task.get_role_tasks(self.request.user.id, app, role)
        return data

    def get_task_object(self):
        ti = self.get_object()
        if ti:
            return Task.objects.filter(id=ti.id).get()
        return None

    @action(detail=False)
    def get_qty(self, request, pk=None):
        qs = self.get_queryset()
        qty = 0
        if qs:
            qty = len(qs)
        return Response({'qty': qty})
    
    def _get_info(self, task):
        if (task.app_task == const.NUM_ROLE_TODO):
            task.get_info()
        if (task.app_note == const.NUM_ROLE_NOTE):
            note_get_info(task)
        if (task.app_news == const.NUM_ROLE_NEWS):
            news_get_info(task)
        if (task.app_store == const.NUM_ROLE_STORE):
            store_get_info(task)
        if (task.app_apart == const.NUM_ROLE_APART):
            apart_get_info(task)
        if (task.app_apart == const.NUM_ROLE_PRICE):
            price_get_info(task)
        if (task.app_apart == const.NUM_ROLE_METER):
            meter_get_info(task)
        if (task.app_apart == const.NUM_ROLE_BILL):
            bill_get_info(task)
        if (task.app_health == const.NUM_ROLE_MARKER):
            marker_get_info(task)
        if (task.app_health == const.NUM_ROLE_INCIDENT):
            incident_get_info(task)
        if (task.app_warr == const.NUM_ROLE_WARR):
            warr_get_info(task)
        if (task.app_expen == const.NUM_ROLE_EXPENSE):
            expen_get_info(task)
        if (task.app_fuel == const.NUM_ROLE_CAR):
            car_get_info(task)
        if (task.app_fuel == const.NUM_ROLE_FUEL):
            fuel_get_info(task)
        if (task.app_fuel == const.NUM_ROLE_PART):
            part_get_info(task)
        if (task.app_fuel == const.NUM_ROLE_SERVICE):
            serv_get_info(task)

    @action(detail=False)
    def get_info(self, request, pk=None):
        for task in Task.objects.filter(user=request.user.id):
            self._get_info(task)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def add_item(self, request, pk=None):
        if 'app' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'app'"},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'role' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'role'"},
                            status=status.HTTP_400_BAD_REQUEST)
        app = self.request.query_params['app']
        role = self.request.query_params['role']
        name = ''
        if 'name' in self.request.query_params:
            name = self.request.query_params['name']
        if Task.use_name(app, role):
            if (not name):
                return Response({"Error": "For application '" + app + "' and role '" + role + "' expected parameter 'name'.\n" + 
                                    "Check Task.use_name() method"},
                                status=status.HTTP_400_BAD_REQUEST)
        group = None
        group_id = None
        if 'group_id' in self.request.query_params:
            group_id = int(self.request.query_params['group_id'])
            if Group.objects.filter(user=request.user.id, id=group_id).exists():
                group = Group.objects.filter(user=request.user.id, id=group_id).get()
        service_id = 0
        if 'service_id' in self.request.query_params:
            service_id = int(self.request.query_params['service_id'])
        task = None
        part_id = 0
        if 'part_id' in self.request.query_params:
            part_id = int(self.request.query_params['part_id'])
        task = None
        message = ''
        ani = Task.get_active_nav_item(request.user.id, app)
        if (app == const.APP_TODO) and (role == const.ROLE_TODO):
            in_my_day = False
            important = False
            stop = None
            if group and (group.determinator == 'view') and (group.view_id == 'myday'):
                in_my_day = True
            if group and (group.determinator == 'view') and (group.view_id == 'important'):
                important = True
            if group and (group.determinator == 'view') and (group.view_id == 'planned'):
                stop = datetime.now().replace(hour=9, minute=0, second=0) + timedelta(1)
            task = Task.objects.create(user=request.user, app_task=const.NUM_ROLE_TODO, name=name, in_my_day=in_my_day, important=important, stop=stop, repeat_days=0)
        match (app, role):
            case (const.APP_NOTE, const.ROLE_NOTE):
                task = Task.objects.create(user=request.user, app_note=const.NUM_ROLE_NOTE, name=name, event=datetime.now())
            case (const.APP_NEWS, const.ROLE_NEWS):
                task = Task.objects.create(user=request.user, app_news=const.NUM_ROLE_NEWS, name=name, event=datetime.now())
            case (const.APP_STORE, const.ROLE_STORE):
                task = add_store(request.user, name)
            case (const.APP_DOCS, const.ROLE_DOC):
                task = Task.objects.create(user=request.user, app_doc=const.NUM_ROLE_DOC, name=name, event=datetime.now())
            case (const.APP_WARR, const.ROLE_WARR):
                task = Task.objects.create(user=request.user, app_warr=const.NUM_ROLE_WARR, name=name, event=datetime.now())
            case (const.APP_EXPEN, const.ROLE_EXPENSE):
                task = Task.objects.create(user=request.user, app_expen=const.NUM_ROLE_EXPENSE, name=name, event=datetime.now())
            case (const.APP_TRIP, const.ROLE_PERSON):
                task = Task.objects.create(user=request.user, app_trip=const.NUM_ROLE_PERSON, name=name, event=datetime.now())
            case (const.APP_TRIP, const.ROLE_TRIP):
                task = Task.objects.create(user=request.user, app_trip=const.NUM_ROLE_TRIP, name=name, event=datetime.now())
            case (const.APP_TRIP, const.ROLE_SALDO):
                task = Task.objects.create(user=request.user, app_trip=const.NUM_ROLE_SALDO, name=name, event=datetime.now())
            case (const.APP_FUEL, const.ROLE_CAR):
                task = Task.objects.create(user=request.user, app_fuel=const.NUM_ROLE_CAR, name=name, event=datetime.now())
            case (const.APP_FUEL, const.ROLE_FUEL):
                task = add_fuel(request.user, ani)
            case (const.APP_FUEL, const.ROLE_PART):
                task = add_part(request.user, ani, name)
            case (const.APP_FUEL, const.ROLE_SERVICE):
                task = add_serv(request.user, ani, part_id)
            case (const.APP_APART, const.ROLE_APART):
                task = Task.objects.create(user=request.user, app_apart=const.NUM_ROLE_APART, name=name, event=datetime.now())
            case (const.APP_APART, const.ROLE_METER):
                task = add_meter(request.user, ani)
            case (const.APP_APART, const.ROLE_PRICE):
                task = add_price(request.user, ani, service_id)
            case (const.APP_APART, const.ROLE_BILL):
                task, message = add_bill(request.user, ani)
            case (const.APP_HEALTH, const.ROLE_MARKER):
                task = add_marker(request.user, name)
            case (const.APP_HEALTH, const.ROLE_INCIDENT):
                task = Task.objects.create(user=request.user, app_health=const.NUM_ROLE_INCIDENT, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_PERIOD):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_PERIOD, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_DEPARTMENT):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_DEPARTMENT, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_DEP_HIST):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_DEP_HIST, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_POST):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_POST, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_EMPLOYEE):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_EMPLOYEE, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_FIO_HIST):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_FIO_HIST, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_CHILDREN):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_CHILD, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_APPOINTMENT):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_APPOINTMENT, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_EDUCATION):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_EDUCATION, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_EMPLOYEE_PERIOD):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_EMPL_PER, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_PAY_TITLE):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_PAY_TITLE, name=name, event=datetime.now())
            case (const.APP_WORK, const.ROLE_PAYMENT):
                task = Task.objects.create(user=request.user, app_work=const.NUM_ROLE_PAYMENT, name=name, event=datetime.now())
            case (const.APP_PHOTO, const.ROLE_PHOTO):
                task = Task.objects.create(user=request.user, app_photo=const.NUM_ROLE_PHOTO, name=name, event=datetime.now())
        if not task:
            return Response({'task_id': 0, 'mess': message})
        task.correct_groups_qty(GIQ_ADD_TASK, group.id)
        self._get_info(task)
        return Response({'task_id': task.id})

    # OK
    @action(detail=False)
    def by_role(self, request, pk=None):
        if 'role' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'role'"},
                            status=status.HTTP_400_BAD_REQUEST)
        role = self.request.query_params['role']
        if role not in const.ALL_ROLES:
            return Response({'Error': "The 'role' parameter must have one of the following values: " + ', '.join(const.ALL_ROLES)},
                            status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # OK
    @action(detail=True)
    def important(self, request, pk=None):
        task = self.get_task_object()
        task.important = not task.important
        self.save(task)
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # OK
    @action(detail=True)
    def in_my_day(self, request, pk=None):
        task = self.get_task_object()
        task.in_my_day = not task.in_my_day
        self.save(task)
        return Response({'title': task.s_in_my_day(), 'value': task.in_my_day})

    # OK
    @action(detail=True)
    def completed(self, request, pk=None):
        task = self.get_task_object()
        next_task = task.toggle_completed()
        self.save(task)
        mess = None
        if next_task:
            next_task.get_info()
            mess = _('replanned to ' + nice_date(next_task.stop))
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response({'data': serializer.data, 'info': mess})


    # OK
    @action(detail=True)
    def category_add(self, request, pk=None):
        if 'category' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'category'"},
                            status=status.HTTP_400_BAD_REQUEST)
        category = self.request.query_params['category']
        task = self.get_task_object()
        cats = task.categories.split()
        cats.append(category)
        task.categories = ' '.join(cats)
        self.save(task)
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # OK
    @action(detail=True)
    def category_delete(self, request, pk=None):
        if 'category' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'category'"},
                            status=status.HTTP_400_BAD_REQUEST)
        category = self.request.query_params['category']
        task = self.get_task_object()
        cats = task.categories.split()
        if category not in cats:
            return Response({'Error': 'There is no such category in this task'},
                            status=status.HTTP_400_BAD_REQUEST)
        cats.remove(category)
        task.categories = ' '.join(cats)
        self.save(task)
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # TODO
    @action(detail=True)
    def file_upload(self, request, pk=None):
        task = self.get_task_object()
        self.save(task)
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # TODO
    @action(detail=True)
    def file_delete(self, request, pk=None):
        if 'app' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'app'"},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'role' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'role'"},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'fname' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'fname'"},
                            status=status.HTTP_400_BAD_REQUEST)
        app = self.request.query_params['app']
        role = self.request.query_params['role']
        fname = self.request.query_params['fname']
        task = self.get_task_object()
        path = task.get_attach_path(role)
        if not os.path.isfile(path + fname):
            return Response({'Error': "The specified file does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)
        os.remove(path + fname)
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # OK
    @action(detail=True)
    def remind_today(self, request, pk=None):
        task = self.get_task_object()
        remind_today = datetime.now()
        remind_today += timedelta(hours = 2)
        if (remind_today.minute > 0):
            correct_min = -remind_today.minute
            if (remind_today.minute > 30):
                correct_min = 60 - remind_today.minute
            remind_today += timedelta(minutes = correct_min)
        task.remind = remind_today
        self.save(task)
        return Response({'date': task.remind_date(), 'time': task.remind_time()})

    # OK
    @action(detail=True)
    def remind_tomorrow(self, request, pk=None):
        task = self.get_task_object()
        task.remind = datetime.now().replace(hour = 9, minute = 0, second = 0) + timedelta(1)
        self.save(task)
        return Response({'date': task.remind_date(), 'time': task.remind_time()})

    # OK
    @action(detail=True)
    def remind_next_week(self, request, pk=None):
        task = self.get_task_object()
        task.remind = datetime.now().replace(hour = 9, minute = 0, second = 0) + timedelta(8 - datetime.today().isoweekday())
        self.save(task)
        return Response({'date': task.remind_date(), 'time': task.remind_time()})

    # OK
    @action(detail=True)
    def remind_delete(self, request, pk=None):
        task = self.get_task_object()
        task.remind = None
        self.save(task)
        return Response({'date': task.remind_date(), 'time': task.remind_time()})

    # OK
    @action(detail=True, url_path='remind_set/(?P<dt>\S+)/(?P<tm>\S+)')
    def remind_set(self, request, pk=None, *args, **kwargs):
        task = self.get_task_object()
        task.remind = datetime.strptime(kwargs['dt'] + "T" + kwargs['tm'], "%d.%m.%YT%H:%M:%S")
        self.save(task)
        return Response({'date': task.remind_date(), 'time': task.remind_time()})

    # OK
    @action(detail=True)
    def termin_today(self, request, pk=None):
        task = self.get_task_object()
        termin_today = datetime.now()
        termin_today += timedelta(hours = 3)
        if (termin_today.minute > 0):
            correct_min = -termin_today.minute
            if (termin_today.minute > 30):
                correct_min = 60 - termin_today.minute
            termin_today += timedelta(minutes = correct_min)
        task.stop = termin_today
        self.save(task)
        return Response({'date': task.termin_date(), 'time': task.termin_time()})

    # OK
    @action(detail=True)
    def termin_tomorrow(self, request, pk=None):
        task = self.get_task_object()
        task.stop = datetime.now().replace(hour = 9, minute = 0, second = 0) + timedelta(1)
        self.save(task)
        return Response({'date': task.termin_date(), 'time': task.termin_time()})

    # OK
    @action(detail=True)
    def termin_next_week(self, request, pk=None):
        task = self.get_task_object()
        task.stop = datetime.now().replace(hour = 9, minute = 0, second = 0) + timedelta(8 - datetime.today().isoweekday())
        self.save(task)
        return Response({'date': task.termin_date(), 'time': task.termin_time()})

    # OK
    @action(detail=True)
    def termin_delete(self, request, pk=None):
        task = self.get_task_object()
        task.stop = None
        if task.repeat != 0:
            task.repeat = 0
        self.save(task)
        return Response({'date': task.termin_date(), 'time': task.termin_time()})

    # OK
    @action(detail=True, url_path='termin_set/(?P<dt>\S+)/(?P<tm>\S+)')
    def termin_set(self, request, pk=None, *args, **kwargs):
        task = self.get_task_object()
        task.stop = datetime.strptime(kwargs['dt'] + "T" + kwargs['tm'], "%d.%m.%YT%H:%M:%S")
        self.save(task)
        return Response({'date': task.termin_date(), 'time': task.termin_time()})

    # OK
    @action(detail=True)
    def repeat_daily(self, request, pk=None):
        task = self.get_task_object()
        task.repeat = const.DAILY
        task.repeat_num = 1
        if not task.stop:
            task.stop = datetime.today().date()
        self.save(task)
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def repeat_workdays(self, request, pk=None):
        task = self.get_task_object()
        task.repeat = const.WEEKLY
        task.repeat_num = 1
        task.repeat_days = 1+2+4+8+16
        if not task.stop:
            task.stop = datetime.today().date()
        self.save(task)
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def repeat_weekly(self, request, pk=None):
        task = self.get_task_object()
        task.repeat = const.WEEKLY
        task.repeat_num = 1
        task.repeat_days = 0
        if not task.stop:
            task.stop = datetime.today().date()
        self.save(task)
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def repeat_monthly(self, request, pk=None):
        task = self.get_task_object()
        task.repeat = const.MONTHLY
        task.repeat_num = 1
        if not task.stop:
            task.stop = datetime.today().date()
        self.save(task)
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def repeat_annually(self, request, pk=None):
        task = self.get_task_object()
        task.repeat = const.ANNUALLY
        task.repeat_num = 1
        if not task.stop:
            task.stop = datetime.today().date()
        self.save(task)
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def repeat_delete(self, request, pk=None):
        task = self.get_task_object()
        task.repeat = 0
        self.save(task)
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True, url_path='repeat_set/(?P<num>\d+)/(?P<per>\d)/(?P<days>\d+)')
    def repeat_set(self, request, pk=None, *args, **kwargs):
        task = self.get_task_object()
        task.repeat = int(kwargs['per'])
        task.repeat_num = int(kwargs['num'])
        task.repeat_days = int(kwargs['days'])
        if not task.stop:
            task.stop = datetime.today().date()
        self.save(task)
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def url_add(self, request, pk=None):
        task = self.get_task_object()
        self.save(task)
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # TODO
    @action(detail=True)
    def url_delete(self, request, pk=None):
        task = self.get_task_object()
        self.save(task)
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # OK
    @action(detail=True)
    def role_add(self, request, pk=None):
        if 'role' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'role'"},
                            status=status.HTTP_400_BAD_REQUEST)
        role = self.request.query_params['role']
        if role not in const.ALL_ROLES:
            return Response({'Error': "The 'role' parameter must have one of the following values: " + ', '.join(const.ALL_ROLES)},
                            status=status.HTTP_400_BAD_REQUEST)
        queryset = Task.objects.filter(user=request.user)
        task = get_object_or_404(queryset, pk=pk)
        match role:
            case const.ROLE_TODO: 
                task.app_task = const.NUM_ROLE_TODO
                task.repeat_days = 0
            case const.ROLE_NOTE: 
                task.app_note = const.NUM_ROLE_NOTE
                if not task.event:
                    task.event = datetime.now()
            case const.ROLE_NEWS: 
                task.app_news = const.NUM_ROLE_NEWS
                if not task.event:
                    task.event = datetime.now()
            case const.ROLE_STORE: task.app_store = const.NUM_ROLE_STORE
            case const.ROLE_DOC: task.app_doc = const.NUM_ROLE_DOC
            case const.ROLE_WARR: task.app_warr = const.NUM_ROLE_WARR
            case const.ROLE_EXPENSE: task.app_expen = const.NUM_ROLE_EXPENSE
            case const.ROLE_SALDO: task.app_expen = const.NUM_ROLE_SALDO
            case const.ROLE_PERSON: task.app_trip = const.NUM_ROLE_PERSON
            case const.ROLE_TRIP: task.app_trip = const.NUM_ROLE_TRIP
            case const.ROLE_FUEL: task.app_fuel = const.NUM_ROLE_FUEL
            case const.ROLE_PART: task.app_fuel = const.NUM_ROLE_PART
            case const.ROLE_SERVICE: task.app_fuel = const.NUM_ROLE_SERVICE
            case const.ROLE_METER: task.app_apart = const.NUM_ROLE_METER
            case const.ROLE_PRICE: task.app_apart = const.NUM_ROLE_PRICE
            case const.ROLE_BILL: task.app_apart = const.NUM_ROLE_BILL
            case const.ROLE_MARKER: task.app_health = const.NUM_ROLE_MARKER
            case const.ROLE_INCIDENT: task.app_health = const.NUM_ROLE_INCIDENT
            case const.ROLE_PERIOD: task.app_work = const.NUM_ROLE_PERIOD
            case const.ROLE_DEPARTMENT: task.app_work = const.NUM_ROLE_DEPARTMENT
            case const.ROLE_DEP_HIST: task.app_work = const.NUM_ROLE_DEP_HIST
            case const.ROLE_POST: task.app_work = const.NUM_ROLE_POST
            case const.ROLE_EMPLOYEE: task.app_work = const.NUM_ROLE_EMPLOYEE
            case const.ROLE_FIO_HIST: task.app_work = const.NUM_ROLE_FIO_HIST
            case const.ROLE_CHILDREN: task.app_work = const.NUM_ROLE_CHILD
            case const.ROLE_APPOINTMENT: task.app_work = const.NUM_ROLE_APPOINTMENT
            case const.ROLE_EDUCATION: task.app_work = const.NUM_ROLE_EDUCATION
            case const.ROLE_EMPLOYEE_PERIOD: task.app_work = const.NUM_ROLE_EMPL_PER
            case const.ROLE_PAY_TITLE: task.app_work = const.NUM_ROLE_PAY_TITLE
            case const.ROLE_PAYMENT: task.app_work = const.NUM_ROLE_PAYMENT
            case const.ROLE_PHOTO: task.app_photo = const.NUM_ROLE_PHOTO
        self.save(task, role)
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)


    # 
    @action(detail=True)
    def role_delete(self, request, pk=None):
        if 'role' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'role'"},
                            status=status.HTTP_400_BAD_REQUEST)
        role = self.request.query_params['role']
        if role not in const.ALL_ROLES:
            return Response({'Error': "The 'role' parameter must have one of the following values: " + ', '.join(const.ALL_ROLES)},
                            status=status.HTTP_400_BAD_REQUEST)
        queryset = Task.objects.filter(user=request.user)
        task = get_object_or_404(queryset, pk=pk)

        match role:
            case const.ROLE_TODO: task.app_task = 0
            case const.ROLE_NOTE: task.app_note = 0
            case const.ROLE_NEWS: task.app_news = 0
            case const.ROLE_STORE: task.app_store = 0
            case const.ROLE_DOC: task.app_doc = 0
            case const.ROLE_WARR: task.app_warr = 0
            case const.ROLE_EXPENSE: task.app_expen = 0
            case const.ROLE_PERSON | const.ROLE_TRIP | const.ROLE_SALDO: task.app_trip = 0
            case const.ROLE_FUEL | const.ROLE_PART | const.ROLE_SERVICE: task.app_fuel = 0
            case const.ROLE_APART | const.ROLE_METER | const.ROLE_PRICE | const.ROLE_BILL: task.app_apart = 0
            case const.ROLE_MARKER | const.ROLE_INCIDENT: task.app_health = 0
            case const.ROLE_PERIOD | const.ROLE_DEPARTMENT | const.ROLE_DEP_HIST | const.ROLE_POST | const.ROLE_EMPLOYEE | const.ROLE_FIO_HIST | const.ROLE_CHILDREN | const.ROLE_APPOINTMENT | const.ROLE_EDUCATION | const.ROLE_EMPLOYEE_PERIOD | const.ROLE_PAY_TITLE | const.ROLE_PAYMENT: task.app_work = 0
            case const.ROLE_PHOTO: task.app_photo = 0

        for tg in TaskGroup.objects.filter(task_id=task.id, role=role):
            task.correct_groups_qty(GIQ_DEL_TASK, role=role)

        if ((task.app_task + task.app_note + task.app_news + task.app_store + task.app_doc + task.app_warr + task.app_expen + 
            task.app_trip + task.app_fuel + task.app_apart + task.app_health + task.app_work + task.app_photo) == 0):
            task.delete_linked_items()
            task.delete()
        else:
            self.save(task)
        
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    def save(self, task, role=const.APP_TODO):
        task.save()
        task.get_info()

    @action(detail=False)
    def check_background_services(self, request, pk=None):
        started = False
        if 'started' in request.query_params:
            started = True
        ret = check_services(started)
        return Response(ret)

    @action(detail=False)
    def actualize_taskroleinfo(self, request, pk=None):
        for task in Task.objects.all():
            self._get_info(task)
        return Response({'result': 'ok'})
        return Response(ret)

    @action(detail=False)
    def correct_expen_amount(self, request, pk=None):
        ret = Task.correct_expen_amount()
        return Response(ret)

    @action(detail=False)
    def update_exchange_rate(self, request, pk=None):
        ret = Task.update_exchange_rate()
        return Response(ret)

    @action(detail=False)
    def get_exchange_rate(self, request, pk=None):
        ret_status = status.HTTP_400_BAD_REQUEST
        if 'currency' not in request.query_params:
            return Response({'result': 'error', 'info': "The 'currency' parameter expected"}, status=ret_status)
        currency = request.query_params['currency']
        if 'date' not in request.query_params:
            return Response({'result': 'error', 'info': "The 'date' parameter expected"}, status=ret_status)
        s_date = request.query_params['date']
        try:
            date = datetime.strptime(s_date, '%Y-%m-%d')
        except:
            return Response({'result': 'error', 'info': "The 'date' paramener must be in the format 'YYYY-MM-DD'"}, status=ret_status)

        if CurrencyRate.objects.filter(currency=currency, date=date).exists():
            cr = CurrencyRate.objects.filter(currency=currency, date=date).get()
            return Response({'result': 'ok', 'num_units': cr.num_units, 'rate_usd': cr.rate_usd})

        api_url = os.environ.get('API_CURR_RATE', '')
        if not api_url:
            return Response({'result': 'error', 'info': "API_CURR_RATE environment variable not set"}, status=ret_status)
        token = os.environ.get('API_CURR_TOKEN', '')
        if not token:
            return Response({'result': 'error', 'info': "API_CURR_TOKEN environment variable not set"}, status=ret_status)
        if '{currency}' not in api_url or '{date}' not in api_url or '{token}' not in api_url:
            return Response({'result': 'error', 'info': "The value of the API_CURR_RATE environment variable does not contain the expected substrings '{token}', '{currency}' and '{date}'"}, status=ret_status)
        url = api_url.replace('{token}', token).replace('{currency}', currency).replace('{date}', s_date)
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers)
        if (resp.status_code != 200):
            ret = json.loads(resp.content)
            ret['result'] = 'error'
            ret_status = resp.status_code
        else:
            try:
                value = json.loads(resp.content)
                rate_usd = value['data'][currency]['value']
                if rate_usd:
                    ret = {'result': 'ok', 'num_units': 1, 'rate_usd': rate_usd}
                    ret_status = status.HTTP_200_OK
                    CurrencyRate.objects.create(currency=currency, date=date, num_units=1, rate_usd=rate_usd)
                else:
                    info = 'Zero rate in responce from call to API_CURR_RATE. ' + str(resp.content)
                    ret = {'result': 'warning', 'info': info}
            except:
                ret = json.loads(resp.content)
                ret['result'] = 'error'
        return Response(ret, status=ret_status)
    