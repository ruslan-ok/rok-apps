import os.path

from datetime import date, datetime, timedelta
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from rest_framework import viewsets, permissions, renderers, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse

from task.const import *
from task.models import Task, TaskGroup
from task.files import storage_path
from api.serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        data = Task.objects.filter(user=self.request.user).order_by('-created')
        if 'role' in self.request.query_params:
            role = self.request.query_params['role']
            if (role == ROLE_TODO):
                return data.filter(app_task=TASK)
            if (role == ROLE_NOTE):
                return data.filter(app_note=NOTE)
            if (role == ROLE_NEWS):
                return data.filter(app_news=NEWS)
            if (role == ROLE_STORE):
                return data.filter(app_store=STORE)
            if (role == ROLE_DOC):
                return data.filter(app_doc=DOC)
            if (role == ROLE_WARR):
                return data.filter(app_warr=WARR)
            if (role == ROLE_EXPEN):
                return data.filter(app_expen=OPERATION)
            if (role == ROLE_EXPEN_SALDO):
                return data.filter(app_expen=SALDO)
            if (role == ROLE_TRIP_PERS):
                return data.filter(app_trip=PERSON)
            if (role == ROLE_TRIP):
                return data.filter(app_trip=TRIP)
            if (role == ROLE_TRIP_SALDO):
                return data.filter(app_trip=SALDO)
            if (role == ROLE_FUEL):
                return data.filter(app_fuel=FUEL)
            if (role == ROLE_FUEL_PART):
                return data.filter(app_fuel=PART)
            if (role == ROLE_FUEL_SERV):
                return data.filter(app_fuel=SERVICE)
            if (role == ROLE_APART_SERV):
                return data.filter(app_apart=SERVICE)
            if (role == ROLE_APART_METER):
                return data.filter(app_apart=METER)
            if (role == ROLE_APART_PRICE):
                return data.filter(app_apart=PRICE)
            if (role == ROLE_APART_BILL):
                return data.filter(app_apart=BILL)
            if (role == ROLE_HEALTH_MARKER):
                return data.filter(app_health=MARKER)
            if (role == ROLE_HEALTH_INCIDENT):
                return data.filter(app_health=INCIDENT)
            if (role == ROLE_HEALTH_ANAMNESIS):
                return data.filter(app_health=ANAMNESIS)
            if (role == ROLE_WORK_PERIOD):
                return data.filter(app_work=PERIOD)
            if (role == ROLE_WORK_DEPART):
                return data.filter(app_work=DEPARTMENT)
            if (role == ROLE_WORK_DEP_HIST):
                return data.filter(app_work=DEP_HIST)
            if (role == ROLE_WORK_POST):
                return data.filter(app_work=POST)
            if (role == ROLE_WORK_EMPL):
                return data.filter(app_work=EMPLOYEE)
            if (role == ROLE_WORK_FIO_HIST):
                return data.filter(app_work=FIO_HIST)
            if (role == ROLE_WORK_CHILD):
                return data.filter(app_work=CHILD)
            if (role == ROLE_WORK_APPOINT):
                return data.filter(app_work=APPOINTMENT)
            if (role == ROLE_WORK_EDUCAT):
                return data.filter(app_work=EDUCATION)
            if (role == ROLE_WORK_EMPL_PER):
                return data.filter(app_work=EMPL_PER)
            if (role == ROLE_WORK_PAY_TITLE):
                return data.filter(app_work=PAY_TITLE)
            if (role == ROLE_WORK_PAYMENT):
                return data.filter(app_work=PAYMENT)
            if (role == ROLE_PHOTO):
                return data.filter(app_photo=PHOTO)
        return data

    # OK
    @action(detail=False)
    def get_qty(self, request, pk=None):
        qty = len(self.get_queryset())
        return Response({'qty': qty})
    
    # OK
    @action(detail=False)
    def by_role(self, request, pk=None):
        if 'role' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'role'"},
                            status=status.HTTP_400_BAD_REQUEST)
        role = self.request.query_params['role']
        if role not in ALL_ROLES:
            return Response({'Error': "The 'role' parameter must have one of the following values: " + ', '.join(ALL_ROLES)},
                            status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    # OK
    @action(detail=True)
    def important(self, request, pk=None):
        task = self.get_object()
        task.important = not task.important
        task.save()
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # OK
    @action(detail=True)
    def in_my_day(self, request, pk=None):
        task = self.get_object()
        task.in_my_day = not task.in_my_day
        task.save()
        return Response({'title': task.s_in_my_day(), 'value': task.in_my_day})

    # OK
    @action(detail=True)
    def completed(self, request, pk=None):
        task = self.get_object()
        task.toggle_completed()
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)


    # OK
    @action(detail=True)
    def category_add(self, request, pk=None):
        if 'category' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'category'"},
                            status=status.HTTP_400_BAD_REQUEST)
        category = self.request.query_params['category']
        task = self.get_object()
        cats = task.categories.split()
        cats.append(category)
        task.categories = ' '.join(cats)
        task.save()
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # OK
    @action(detail=True)
    def category_delete(self, request, pk=None):
        if 'category' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'category'"},
                            status=status.HTTP_400_BAD_REQUEST)
        category = self.request.query_params['category']
        task = self.get_object()
        cats = task.categories.split()
        if category not in cats:
            return Response({'Error': 'There is no such category in this task'},
                            status=status.HTTP_400_BAD_REQUEST)
        cats.remove(category)
        task.categories = ' '.join(cats)
        task.save()
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # TODO
    @action(detail=True)
    def file_upload(self, request, pk=None):
        task = self.get_object()
        task.save()
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
        task = self.get_object()
        path = storage_path.format(self.request.user.id) + '{}/{}_{}/'.format(app, role, task.id)
        if not os.path.isfile(path + fname[4:]):
            return Response({'Error': "The specified file does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)
        os.remove(path + fname[4:])
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # OK
    @action(detail=True)
    def remind_today(self, request, pk=None):
        task = self.get_object()
        remind_today = datetime.now()
        remind_today += timedelta(hours = 3)
        if (remind_today.minute > 0):
            correct_min = -remind_today.minute
            if (remind_today.minute > 30):
                correct_min = 60 - remind_today.minute
            remind_today += timedelta(minutes = correct_min)
        task.remind = remind_today
        task.save()
        return Response({'date': task.remind_date(), 'time': task.remind_time()})

    # OK
    @action(detail=True)
    def remind_tomorrow(self, request, pk=None):
        task = self.get_object()
        task.remind = datetime.now().replace(hour = 9, minute = 0, second = 0) + timedelta(1)
        task.save()
        return Response({'date': task.remind_date(), 'time': task.remind_time()})

    # OK
    @action(detail=True)
    def remind_next_week(self, request, pk=None):
        task = self.get_object()
        task.remind = datetime.now().replace(hour = 9, minute = 0, second = 0) + timedelta(8 - datetime.today().isoweekday())
        task.save()
        return Response({'date': task.remind_date(), 'time': task.remind_time()})

    # OK
    @action(detail=True)
    def remind_delete(self, request, pk=None):
        task = self.get_object()
        task.remind = None
        task.save()
        return Response({'date': task.remind_date(), 'time': task.remind_time()})

    # OK
    @action(detail=True, url_path='remind_set/(?P<dt>\S+)/(?P<tm>\S+)')
    def remind_set(self, request, pk=None, *args, **kwargs):
        task = self.get_object()
        task.remind = datetime.strptime(kwargs['dt'] + "T" + kwargs['tm'], "%d.%m.%YT%H:%M:%S")
        task.save()
        return Response({'date': task.remind_date(), 'time': task.remind_time()})

    # OK
    @action(detail=True)
    def termin_today(self, request, pk=None):
        task = self.get_object()
        task.stop = datetime.today()
        task.save()
        return Response({'date': task.termin_date(), 'time': task.termin_time()})

    # OK
    @action(detail=True)
    def termin_tomorrow(self, request, pk=None):
        task = self.get_object()
        task.stop = datetime.today() + timedelta(1)
        task.save()
        return Response({'date': task.termin_date(), 'time': task.termin_time()})

    # OK
    @action(detail=True)
    def termin_next_week(self, request, pk=None):
        task = self.get_object()
        task.stop = datetime.today() + timedelta(8 - datetime.today().isoweekday())
        task.save()
        return Response({'date': task.termin_date(), 'time': task.termin_time()})

    # OK
    @action(detail=True)
    def termin_delete(self, request, pk=None):
        task = self.get_object()
        task.stop = None
        if task.repeat != 0:
            task.repeat = 0
        task.save()
        return Response({'date': task.termin_date(), 'time': task.termin_time()})

    # OK
    @action(detail=True, url_path='termin_set/(?P<dt>\S+)/(?P<tm>\S+)')
    def termin_set(self, request, pk=None, *args, **kwargs):
        task = self.get_object()
        task.stop = datetime.strptime(kwargs['dt'] + "T" + kwargs['tm'], "%d.%m.%YT%H:%M:%S")
        task.save()
        return Response({'date': task.termin_date(), 'time': task.termin_time()})

    # OK
    @action(detail=True)
    def repeat_daily(self, request, pk=None):
        task = self.get_object()
        task.repeat = DAILY
        task.repeat_num = 1
        if not task.stop:
            task.stop = datetime.today().date()
        task.save()
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def repeat_workdays(self, request, pk=None):
        task = self.get_object()
        task.repeat = WEEKLY
        task.repeat_num = 1
        task.repeat_days = 1+2+4+8+16
        if not task.stop:
            task.stop = datetime.today().date()
        task.save()
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def repeat_weekly(self, request, pk=None):
        task = self.get_object()
        task.repeat = WEEKLY
        task.repeat_num = 1
        task.repeat_days = 0
        if not task.stop:
            task.stop = datetime.today().date()
        task.save()
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def repeat_monthly(self, request, pk=None):
        task = self.get_object()
        task.repeat = MONTHLY
        task.repeat_num = 1
        if not task.stop:
            task.stop = datetime.today().date()
        task.save()
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def repeat_annually(self, request, pk=None):
        task = self.get_object()
        task.repeat = ANNUALLY
        task.repeat_num = 1
        if not task.stop:
            task.stop = datetime.today().date()
        task.save()
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def repeat_delete(self, request, pk=None):
        task = self.get_object()
        task.repeat = 0
        task.save()
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True, url_path='repeat_set/(?P<num>\d+)/(?P<per>\d)/(?P<days>\d+)')
    def repeat_set(self, request, pk=None, *args, **kwargs):
        task = self.get_object()
        task.repeat = int(kwargs['per'])
        task.repeat_num = int(kwargs['num'])
        task.repeat_days = int(kwargs['days'])
        if not task.stop:
            task.stop = datetime.today().date()
        task.save()
        return Response({'title': task.repeat_title(), 'info': task.repeat_info()})

    # OK
    @action(detail=True)
    def url_add(self, request, pk=None):
        task = self.get_object()
        task.save()
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # TODO
    @action(detail=True)
    def url_delete(self, request, pk=None):
        task = self.get_object()
        task.save()
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

    # OK
    @action(detail=True)
    def role_add(self, request, pk=None):
        if 'role' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'role'"},
                            status=status.HTTP_400_BAD_REQUEST)
        role = self.request.query_params['role']
        if role not in ALL_ROLES:
            return Response({'Error': "The 'role' parameter must have one of the following values: " + ', '.join(ALL_ROLES)},
                            status=status.HTTP_400_BAD_REQUEST)
        queryset = Task.objects.filter(user=request.user)
        task = get_object_or_404(queryset, pk=pk)
        if (role == ROLE_TODO):
            task.app_task = TASK
        if (role == ROLE_NOTE):
            task.app_note = NOTE
        if (role == ROLE_NEWS):
            task.app_news = NEWS
        if (role == ROLE_STORE):
            task.app_store = STORE
        if (role == ROLE_DOC):
            task.app_doc = DOC
        if (role == ROLE_WARR):
            task.app_warr = WARR
        if (role == ROLE_EXPEN):
            task.app_expen = OPERATION
        if (role == ROLE_EXPEN_SALDO):
            task.app_expen = SALDO
        if (role == ROLE_TRIP_PERS):
            task.app_trip = PERSON
        if (role == ROLE_TRIP):
            task.app_trip = TRIP
        if (role == ROLE_TRIP_SALDO):
            task.app_trip = SALDO
        if (role == ROLE_FUEL):
            task.app_fuel = FUEL
        if (role == ROLE_FUEL_PART):
            task.app_fuel = PART
        if (role == ROLE_FUEL_SERV):
            task.app_fuel = SERVICE
        if (role == ROLE_APART_SERV):
            task.app_apart = SERVICE
        if (role == ROLE_APART_METER):
            task.app_apart = METER
        if (role == ROLE_APART_PRICE):
            task.app_apart = PRICE
        if (role == ROLE_APART_BILL):
            task.app_apart = BILL
        if (role == ROLE_HEALTH_MARKER):
            task.app_health = MARKER
        if (role == ROLE_HEALTH_INCIDENT):
            task.app_health = INCIDENT
        if (role == ROLE_HEALTH_ANAMNESIS):
            task.app_health = ANAMNESIS
        if (role == ROLE_WORK_PERIOD):
            task.app_work = PERIOD
        if (role == ROLE_WORK_DEPART):
            task.app_work = DEPARTMENT
        if (role == ROLE_WORK_DEP_HIST):
            task.app_work = DEP_HIST
        if (role == ROLE_WORK_POST):
            task.app_work = POST
        if (role == ROLE_WORK_EMPL):
            task.app_work = EMPLOYEE
        if (role == ROLE_WORK_FIO_HIST):
            task.app_work = FIO_HIST
        if (role == ROLE_WORK_CHILD):
            task.app_work = CHILD
        if (role == ROLE_WORK_APPOINT):
            task.app_work = APPOINTMENT
        if (role == ROLE_WORK_EDUCAT):
            task.app_work = EDUCATION
        if (role == ROLE_WORK_EMPL_PER):
            task.app_work = EMPL_PER
        if (role == ROLE_WORK_PAY_TITLE):
            task.app_work = PAY_TITLE
        if (role == ROLE_WORK_PAYMENT):
            task.app_work = PAYMENT
        if (role == ROLE_PHOTO):
            task.app_photo = PHOTO
        task.save()
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)


    # 
    @action(detail=True)
    def role_delete(self, request, pk=None):
        if 'role' not in self.request.query_params:
            return Response({'Error': "Expected parameter 'role'"},
                            status=status.HTTP_400_BAD_REQUEST)
        role = self.request.query_params['role']
        if role not in ALL_ROLES:
            return Response({'Error': "The 'role' parameter must have one of the following values: " + ', '.join(ALL_ROLES)},
                            status=status.HTTP_400_BAD_REQUEST)
        queryset = Task.objects.filter(user=request.user)
        task = get_object_or_404(queryset, pk=pk)

        if (role == ROLE_TODO):
            task.app_task = NONE
        
        if (role == ROLE_NOTE):
            task.app_note = NONE
        
        if (role == ROLE_NEWS):
            task.app_news = NONE
        
        if (role == ROLE_STORE):
            task.app_store = NONE
        
        if (role == ROLE_DOC):
            task.app_doc = NONE
        
        if (role == ROLE_WARR):
            task.app_warr = NONE
        
        if (role in [ROLE_EXPEN, ROLE_EXPEN_SALDO]):
            task.app_expen = NONE
        
        if (role in [ROLE_TRIP_PERS, ROLE_TRIP, ROLE_TRIP_SALDO]):
            task.app_trip = NONE

        if (role in [ROLE_FUEL, ROLE_FUEL_PART, ROLE_FUEL_SERV]):
            task.app_fuel = NONE

        if (role in [ROLE_APART_SERV, ROLE_APART_METER, ROLE_APART_PRICE, ROLE_APART_BILL]):
            task.app_apart = NONE
        
        if (role in [ROLE_HEALTH_MARKER, ROLE_HEALTH_INCIDENT, ROLE_HEALTH_ANAMNESIS]):
            task.app_health = NONE
        
        if (role in [ROLE_WORK_PERIOD, ROLE_WORK_DEPART, ROLE_WORK_DEP_HIST, ROLE_WORK_POST, ROLE_WORK_EMPL, ROLE_WORK_FIO_HIST,
            ROLE_WORK_CHILD, ROLE_WORK_APPOINT, ROLE_WORK_EDUCAT, ROLE_WORK_EMPL_PER, ROLE_WORK_PAY_TITLE, ROLE_WORK_PAYMENT]):
            task.app_work = NONE
        
        if (role == ROLE_PHOTO):
            task.app_photo = NONE
        
        tgs = TaskGroup.objects.filter(task=task.id, role=role)
        if (len(tgs) > 0):
            tgs.delete()

        if ((task.app_task + task.app_note + task.app_news + task.app_store + task.app_doc + task.app_warr + task.app_expen + 
            task.app_trip + task.app_fuel + task.app_apart + task.app_health + task.app_work + task.app_photo) == 0):
            task.delete()
        else:
            task.save()
        
        serializer = TaskSerializer(instance=task, context={'request': request})
        return Response(serializer.data)

