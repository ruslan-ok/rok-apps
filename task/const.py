from django.utils.translation import gettext_lazy as _

NONE = 0

"""
Kinds of Entities that can be combined into Lists
"""
KIND_TASK = 1 # Tasks Group
KIND_NOTE = 2 # Notes Group
KIND_NEWS = 3 # News Group
KIND_DOC = 4 # Documents Group
KIND_WARR = 5 # Warranties Group
KIND_STORE = 6 # Store Entries Group
KIND_EXPEN = 7 # Project for Expenses
KIND_TRIP = 8 # Trips Group
KIND_CAR = 9 # Car for Fueling, Part and Service
KIND_APART = 10 # Apartment for Service, Meter, Price and Bill
KIND_ANAMN = 11 # Anamnesis for a Health Incident

KIND_CHOICE = [(KIND_TASK, _('tasks')),
               (KIND_NOTE, _('notes')),
               (KIND_NEWS, _('news')),
               (KIND_DOC, _('documents')),
               (KIND_WARR, _('warranties')),
               (KIND_STORE, _('stores')),
               (KIND_EXPEN, _('expenses')),
               (KIND_TRIP, _('trips')),
               (KIND_CAR, _('list is a car')),
               (KIND_APART, _('list is an apartment')),
               (KIND_ANAMN, _('list is an anamnesis')),
              ]

DAILY = 1
WEEKLY = 3
MONTHLY = 4
ANNUALLY = 5

REPEAT_SELECT = [
    (DAILY, _('days')),
    (WEEKLY, _('weeks')),
    (MONTHLY, _('months')),
    (ANNUALLY, _('years')),
]

"""
There are Roles in different Applications
"""
TASK = 1
NOTE = 2
NEWS = 3
STORE = 4
DOC = 5
WARR = 6
OPERATION = 7
SALDO = 8
PERSON = 9
TRIP = 10
FUEL = 12
PART = 13
SERVICE = 14
METER = 16
PRICE = 17 
BILL = 18
MARKER = 19 
INCIDENT = 20 
ANAMNESIS = 21
PERIOD = 22 
DEPARTMENT = 23
DEP_HIST = 24 
POST = 25 
EMPLOYEE = 26
FIO_HIST = 27 
CHILD = 28 
APPOINTMENT = 29
EDUCATION = 30
EMPL_PER = 31 
PAY_TITLE = 32 
PAYMENT = 33 
PHOTO = 34


"""
There are Available Roles for each Application
"""
TASK_ROLE_CHOICE = [(TASK, _('task'))]
NOTE_ROLE_CHOICE = [(NOTE, _('note'))]
NEWS_ROLE_CHOICE = [(NEWS, _('news'))] 
STORE_ROLE_CHOICE = [(STORE, _('store'))]
DOC_ROLE_CHOICE = [(DOC, _('doc'))]
WARR_ROLE_CHOICE = [(WARR, _('warranty'))]
EXPEN_ROLE_CHOICE = [(OPERATION, _('operation')), (SALDO, _('saldo'))]
TRIP_ROLE_CHOICE = [(PERSON, _('person')), (TRIP, _('trip')), (SALDO, _('saldo'))]
FUEL_ROLE_CHOICE = [(FUEL, _('fueling')), (PART, _('car part service interval')),
                    (SERVICE, _('service'))]
APART_ROLE_CHOICE = [(SERVICE, _('service')), (METER, _('meter')),
                     (PRICE, _('price')), (BILL, _('bill'))]
HEALTH_ROLE_CHOICE = [(MARKER, _('marker')), (INCIDENT, _('incident')), (ANAMNESIS, _('anamnesis'))]
WORK_ROLE_CHOICE = [(PERIOD, _('period')), (DEPARTMENT, _('department')), (DEP_HIST, _('department history')), 
                    (POST, _('post')), (EMPLOYEE, _('employee')), (FIO_HIST, _('surname history')), (CHILD, _('child')), 
                    (APPOINTMENT, _('appointment')), (EDUCATION, _('education')), (EMPL_PER, _('periods for employee')),
                    (PAY_TITLE, _('pay tytle')), (PAYMENT, _('payment'))]
PHOTO_ROLE_CHOICE = [(PHOTO, _('photo'))]

