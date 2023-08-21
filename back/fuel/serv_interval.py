import os
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.template import loader
from logs.models import EventType
from service.site_service import SiteService
from account.models import UserExt
from task.const import APP_FUEL, NUM_ROLE_PART, NUM_ROLE_SERVICE, ROLE_PART
from task.models import Task
from fuel.utils import LANG_EN, LANG_RU, get_rest, month_declination

class ServInterval(SiteService):

    def __init__(self, *args, **kwargs):
        super().__init__(APP_FUEL, ROLE_PART, 'Контроль сервисных интервалов обслуживания автомобиля', *args, **kwargs)

    def ripe(self):
        return True, True

    def process(self):
        self.log_event(EventType.INFO, 'start')
        parts = Task.objects.filter(app_fuel=NUM_ROLE_PART)
        users = []
        status = []
        rests = {}
        #dbg = ''
        for part in parts:
            if part.user.username == 'demouser':
                continue
            car = part.task_1
            if not car.car_notice:
                continue
            user_ext = UserExt.objects.filter(user=part.user).get()
            last_odo = None
            last_repl = None
            if Task.objects.filter(user=part.user.id, app_fuel__gt=0, task_1=part.task_1.id).exclude(car_odometr=None).exclude(car_odometr=0).exists():
                last_odo = Task.objects.filter(user=part.user.id, app_fuel__gt=0, task_1=part.task_1.id).exclude(car_odometr=None).exclude(car_odometr=0).order_by('-event')[0]
            if last_odo:
                if Task.objects.filter(user=part.user.id, app_fuel=NUM_ROLE_SERVICE, task_1=part.task_1.id, task_2=part.id).exists():
                    last_repl = Task.objects.filter(user=part.user.id, app_fuel=NUM_ROLE_SERVICE, task_1=part.task_1.id, task_2=part.id).order_by('-event')[0]
            if (last_odo and last_repl):
                if user_ext.lang == 1:
                    lang = LANG_RU
                else:
                    lang = LANG_EN
                rest, tune_class = get_rest(part, last_odo, last_repl, lang)
                tune_class = tune_class.replace('rest-color-', '')
                #dbg += f'   id:{part.id}, rest:"{rest}", class:"{tune_class}."'
                rests[str(part.id)] = {'rest': rest, 'class': tune_class}
                if tune_class == 'normal':
                    if part.fuel_warn or part.fuel_expir:
                        part.fuel_warn = None
                        part.fuel_expir = None
                        part.save()
                elif tune_class == 'warning':
                    if not part.fuel_warn or not user_ext.fuel_notice or ((datetime.now() - user_ext.fuel_notice) >= timedelta(days=7)):
                        if not part.fuel_warn:
                            status.append(part)
                            part.fuel_warn = datetime.now()
                            part.save()
                        if part.user not in users:
                            users.append(part.user)
                elif tune_class == 'error':
                    if not part.fuel_expir or not user_ext.fuel_notice or ((datetime.now() - user_ext.fuel_notice) >= timedelta(days=7)):
                        if not part.fuel_expir:
                            status.append(part)
                            part.fuel_expir = datetime.now()
                            part.save()
                        if part.user not in users:
                            users.append(part.user)
        self.send_notifications(users, status, rests)
        self.log_event(EventType.INFO, 'stop')
        return True

    def send_notifications(self, users, status_parts, rests, dbg=''):
        for user in users:
            user_parts = Task.objects.filter(user=user.id, app_fuel=NUM_ROLE_PART).exclude(fuel_warn=None, fuel_expir=None)
            context = {'cars': []}
            cars = []
            for part in user_parts:
                if part.task_1 not in cars and part.task_1.car_notice:
                    cars.append(part.task_1)
            for car in cars:
                car_info = {'name': car.name, 'parts_1': [], 'parts_2': []}
                for part in user_parts:
                    if car != part.task_1:
                        continue

                    user_ext = UserExt.objects.filter(user=part.user).get()
                    if user_ext.lang == 1:
                        lang = LANG_RU
                    else:
                        lang = LANG_EN

                    if lang == LANG_RU:
                        lbl_km = 'км'
                    else:
                        lbl_km = 'km'

                    part_termin = ''

                    if part.part_chg_km:
                        part_termin = '{} {}'.format(part.part_chg_km, lbl_km)

                    if part.part_chg_mo:
                        if (len(part_termin) > 0):
                            part_termin += ' '
                        part_termin += month_declination(part.part_chg_mo, lang)
                    
                    part_rest = rests[str(part.id)]
                    color = 'tomato'
                    if part_rest['class'] == 'error':
                        color = 'red'

                    if part in status_parts:
                        car_info['parts_1'].append({'name': part.name, 'termin': part_termin, 'color': color, 'rest': part_rest['rest']})
                    else:
                        car_info['parts_2'].append({'name': part.name, 'termin': part_termin, 'color': color, 'rest': part_rest['rest']})

                context['cars'].append(car_info)

            user_ext = UserExt.objects.filter(user=user.id).get()
            if user_ext.lang == 1:
                email_template_name = 'fuel/notification_email_ru.html'
                email_subj = 'Контроль сервисных интервалов'
            else:
                email_template_name = 'fuel/notification_email_en.html'
                email_subj = 'Car Service Interval Notice'
            body = loader.render_to_string(email_template_name, context)
            user_ext.fuel_notice = datetime.now()
            user_ext.save()
            try:
                mail_from = os.environ.get('DJANGO_MAIL_USER')
                msg = EmailMessage(email_subj, body, mail_from, [user.email])
                msg.content_subtype = "html"
                msg.send()
                self.log_event(EventType.INFO, 'notify', user.email + ' - ok')
            except Exception as e:
                self.log_event(EventType.ERROR, 'notify', user.email + ' - exception: ' + str(e))
