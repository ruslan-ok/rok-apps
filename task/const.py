from django.utils.translation import gettext_lazy as _

"""
Apps
"""
APP_HOME = 'home'
APP_TODO = 'todo'
APP_NOTE = 'note'
APP_NEWS = 'news'
APP_STORE = 'store'
APP_DOCS = 'docs'
APP_WARR = 'warr'
APP_EXPEN = 'expen'
APP_TRIP = 'trip'
APP_FUEL = 'fuel'
APP_APART = 'apart'
APP_HEALTH = 'health'
APP_WORK = 'work'
APP_PHOTO = 'photo'
APP_ADMIN = 'admin'

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
WORKDAYS = 2
MONTHLY = 4
ANNUALLY = 5

REPEAT = [
    (NONE, _('no')),
    (DAILY, _('daily')),
    (WORKDAYS, _('work days')),
    (WEEKLY, _('weekly')),
    (MONTHLY, _('monthly')),
    (ANNUALLY, _('annually')),
]

REPEAT_SELECT = [
    (DAILY, _('days')),
    (WEEKLY, _('weeks')),
    (MONTHLY, _('months')),
    (ANNUALLY, _('years')),
]

REPEAT_NAME = {
    DAILY: _('days'),
    WEEKLY: _('weeks'),
    MONTHLY: _('months'),
    ANNUALLY: _('years'),
}

"""
There are Roles in different Applications
"""
NUM_ROLE_TODO = 1
NUM_ROLE_NOTE = 2
NUM_ROLE_NEWS = 3
NUM_ROLE_STORE = 4
NUM_ROLE_DOC = 5
NUM_ROLE_WARR = 6
NUM_ROLE_OPERATION = 7
NUM_ROLE_SALDO = 8
NUM_ROLE_PERSON = 9
NUM_ROLE_TRIP = 10
NUM_ROLE_CAR = 11
NUM_ROLE_FUEL = 12
NUM_ROLE_PART = 13
NUM_ROLE_SERVICE = 14
NUM_ROLE_APART = 15
NUM_ROLE_METER = 16
NUM_ROLE_PRICE = 17 
NUM_ROLE_BILL = 18
NUM_ROLE_MARKER = 19 
NUM_ROLE_INCIDENT = 20 
NUM_ROLE_ANAMNESIS = 21
NUM_ROLE_PERIOD = 22 
NUM_ROLE_DEPARTMENT = 23
NUM_ROLE_DEP_HIST = 24 
NUM_ROLE_POST = 25 
NUM_ROLE_EMPLOYEE = 26
NUM_ROLE_FIO_HIST = 27 
NUM_ROLE_CHILD = 28 
NUM_ROLE_APPOINTMENT = 29
NUM_ROLE_EDUCATION = 30
NUM_ROLE_EMPL_PER = 31 
NUM_ROLE_PAY_TITLE = 32 
NUM_ROLE_PAYMENT = 33 
NUM_ROLE_PHOTO = 34
NUM_ROLE_ACCOUNT = 35

ROLE_TODO        = 'todo'            
ROLE_NOTE        = 'note'            
ROLE_NEWS        = 'news'            
ROLE_STORE       = 'store'           
ROLE_DOC         = 'doc'             
ROLE_WARR        = 'warr'            
ROLE_PROJECT     = 'expen_proj'
ROLE_EXPENSES    = 'expenses'           
ROLE_PERSON      = 'person'       
ROLE_TRIP        = 'trip'            
ROLE_SALDO       = 'saldo'      
ROLE_CAR         = 'car'            
ROLE_FUEL        = 'fuel'            
ROLE_PART        = 'part'       
ROLE_APART       = 'apart'      
ROLE_SERVICE     = 'service'      
ROLE_METER       = 'meter'     
ROLE_PRICE       = 'price'     
ROLE_BILL        = 'bill'      
ROLE_MARKER      = 'marker'   
ROLE_INCIDENT    = 'incident' 
ROLE_ANAMNESIS   = 'anamnesis'
ROLE_PERIOD      = 'period'     
ROLE_DEPARTMENT  = 'department'     
ROLE_DEP_HIST    = 'dep_hist'   
ROLE_POST        = 'post'       
ROLE_EMPLOYEE    = 'employee'       
ROLE_FIO_HIST    = 'fio_hist'   
ROLE_CHILDREN    = 'child'      
ROLE_APPOINTMENT = 'appointment'    
ROLE_EDUCATION   = 'education'     
ROLE_EMPLOYEE_PERIOD = 'empl_per'   
ROLE_PAY_TITLE   = 'pay_title'  
ROLE_PAYMENT     = 'payment'    
ROLE_PHOTO       = 'photo'      
ROLE_ACCOUNT     = 'account'     

ALL_ROLES = (
    ROLE_TODO,             
    ROLE_NOTE,             
    ROLE_NEWS,             
    ROLE_STORE,            
    ROLE_DOC,              
    ROLE_WARR,             
    ROLE_PROJECT,
    ROLE_EXPENSES,            
    ROLE_PERSON,        
    ROLE_TRIP,             
    ROLE_SALDO,       
    ROLE_FUEL,             
    ROLE_PART,
    ROLE_SERVICE,        
    ROLE_APART,       
    ROLE_METER,      
    ROLE_PRICE,      
    ROLE_BILL,       
    ROLE_MARKER,    
    ROLE_INCIDENT,  
    ROLE_ANAMNESIS, 
    ROLE_PERIOD,      
    ROLE_DEPARTMENT,      
    ROLE_DEP_HIST,    
    ROLE_POST,        
    ROLE_EMPLOYEE,        
    ROLE_FIO_HIST,    
    ROLE_CHILDREN,       
    ROLE_APPOINTMENT,     
    ROLE_EDUCATION,      
    ROLE_EMPLOYEE_PERIOD,    
    ROLE_PAY_TITLE,   
    ROLE_PAYMENT,     
    ROLE_PHOTO, 
    ROLE_ACCOUNT,           
    )

ROLES_IDS = {
    APP_HOME: { ROLE_ACCOUNT: NUM_ROLE_ACCOUNT },
    APP_TODO: { ROLE_TODO: NUM_ROLE_TODO },
    APP_NOTE: { ROLE_NOTE: NUM_ROLE_NOTE },
    APP_NEWS: { ROLE_NEWS: NUM_ROLE_NEWS },
    APP_STORE: { ROLE_STORE: NUM_ROLE_STORE },
    APP_DOCS: { ROLE_DOC: NUM_ROLE_DOC },
    APP_WARR: { ROLE_WARR: NUM_ROLE_WARR },
    APP_EXPEN: { ROLE_PROJECT: NUM_ROLE_SALDO, ROLE_EXPENSES: NUM_ROLE_OPERATION },
    APP_TRIP: { ROLE_PERSON: NUM_ROLE_PERSON, ROLE_TRIP: NUM_ROLE_TRIP, ROLE_SALDO: NUM_ROLE_SALDO },
    APP_FUEL: { ROLE_CAR: NUM_ROLE_CAR, ROLE_FUEL: NUM_ROLE_FUEL, ROLE_PART: NUM_ROLE_PART, ROLE_SERVICE: NUM_ROLE_SERVICE },
    APP_APART: { ROLE_APART: NUM_ROLE_APART, ROLE_SERVICE: NUM_ROLE_SERVICE, ROLE_METER: NUM_ROLE_METER, ROLE_PRICE: NUM_ROLE_PRICE, ROLE_BILL: NUM_ROLE_BILL },
    APP_HEALTH: { ROLE_MARKER: NUM_ROLE_MARKER, ROLE_INCIDENT: NUM_ROLE_INCIDENT, ROLE_ANAMNESIS: NUM_ROLE_ANAMNESIS },
    APP_WORK: { ROLE_PERIOD: NUM_ROLE_PERIOD, ROLE_DEPARTMENT: NUM_ROLE_DEPARTMENT, ROLE_DEP_HIST: NUM_ROLE_DEP_HIST, 
                ROLE_POST: NUM_ROLE_POST, ROLE_EMPLOYEE: NUM_ROLE_EMPLOYEE, ROLE_FIO_HIST: NUM_ROLE_FIO_HIST, 
                ROLE_CHILDREN: NUM_ROLE_CHILD, ROLE_APPOINTMENT: NUM_ROLE_APPOINTMENT, ROLE_EDUCATION: NUM_ROLE_EDUCATION, 
                ROLE_EMPLOYEE_PERIOD: NUM_ROLE_EMPL_PER, ROLE_PAY_TITLE: NUM_ROLE_PAY_TITLE, ROLE_PAYMENT: NUM_ROLE_PAYMENT },
    APP_PHOTO: { ROLE_PHOTO: NUM_ROLE_PHOTO },
}

"""
There are Available Roles for each Application
"""
TASK_ROLE_CHOICE   = [(NONE, '--------'), (NUM_ROLE_TODO, _('task'))]
NOTE_ROLE_CHOICE   = [(NONE, '--------'), (NUM_ROLE_NOTE, _('note'))]
NEWS_ROLE_CHOICE   = [(NONE, '--------'), (NUM_ROLE_NEWS, _('news'))] 
STORE_ROLE_CHOICE  = [(NONE, '--------'), (NUM_ROLE_STORE, _('store'))]
DOC_ROLE_CHOICE    = [(NONE, '--------'), (NUM_ROLE_DOC, _('doc'))]
WARR_ROLE_CHOICE   = [(NONE, '--------'), (NUM_ROLE_WARR, _('warranty'))]
EXPEN_ROLE_CHOICE  = [(NONE, '--------'), (NUM_ROLE_OPERATION, _('operation')), (NUM_ROLE_SALDO, _('saldo'))]
TRIP_ROLE_CHOICE   = [(NONE, '--------'), (NUM_ROLE_PERSON, _('person')), (NUM_ROLE_TRIP, _('trip')), (NUM_ROLE_SALDO, _('saldo'))]
FUEL_ROLE_CHOICE   = [(NONE, '--------'), (NUM_ROLE_CAR, _('cars')), (NUM_ROLE_FUEL, _('fueling')), (NUM_ROLE_PART, _('car part service interval')), (NUM_ROLE_SERVICE, _('service'))]
APART_ROLE_CHOICE  = [(NONE, '--------'), (NUM_ROLE_APART, _('apartment')), (NUM_ROLE_SERVICE, _('service')), (NUM_ROLE_METER, _('meter')), (NUM_ROLE_PRICE, _('price')), (NUM_ROLE_BILL, _('bill'))]
HEALTH_ROLE_CHOICE = [(NONE, '--------'), (NUM_ROLE_MARKER, _('marker')), (NUM_ROLE_INCIDENT, _('incident')), (NUM_ROLE_ANAMNESIS, _('anamnesis'))]
WORK_ROLE_CHOICE   = [(NONE, '--------'), (NUM_ROLE_PERIOD, _('period')), (NUM_ROLE_DEPARTMENT, _('department')), (NUM_ROLE_DEP_HIST, _('department history')), 
                        (NUM_ROLE_POST, _('post')), (NUM_ROLE_EMPLOYEE, _('employee')), (NUM_ROLE_FIO_HIST, _('surname history')), (NUM_ROLE_CHILD, _('child')), 
                        (NUM_ROLE_APPOINTMENT, _('appointment')), (NUM_ROLE_EDUCATION, _('education')), (NUM_ROLE_EMPL_PER, _('periods for employee')),
                        (NUM_ROLE_PAY_TITLE, _('pay tytle')), (NUM_ROLE_PAYMENT, _('payment'))]
PHOTO_ROLE_CHOICE  = [(NONE, '--------'), (NUM_ROLE_PHOTO, _('photo'))]

ROLE_BY_NUM = {
    NUM_ROLE_TODO         : ROLE_TODO        , 
    NUM_ROLE_NOTE         : ROLE_NOTE        , 
    NUM_ROLE_NEWS         : ROLE_NEWS        , 
    NUM_ROLE_STORE        : ROLE_STORE       , 
    NUM_ROLE_DOC          : ROLE_DOC         , 
    NUM_ROLE_WARR         : ROLE_WARR        , 
    NUM_ROLE_OPERATION    : ROLE_EXPENSES    , 
    NUM_ROLE_SALDO        : ROLE_SALDO       , 
    NUM_ROLE_PERSON       : ROLE_PERSON      , 
    NUM_ROLE_TRIP         : ROLE_TRIP        , 
    NUM_ROLE_CAR          : ROLE_CAR         , 
    NUM_ROLE_FUEL         : ROLE_FUEL        , 
    NUM_ROLE_PART         : ROLE_PART        , 
    NUM_ROLE_SERVICE      : ROLE_SERVICE     , 
    NUM_ROLE_APART        : ROLE_APART       , 
    NUM_ROLE_METER        : ROLE_METER       , 
    NUM_ROLE_PRICE        : ROLE_PRICE       , 
    NUM_ROLE_BILL         : ROLE_BILL        , 
    NUM_ROLE_MARKER       : ROLE_MARKER      , 
    NUM_ROLE_INCIDENT     : ROLE_INCIDENT    , 
    NUM_ROLE_ANAMNESIS    : ROLE_ANAMNESIS   , 
    NUM_ROLE_PERIOD       : ROLE_PERIOD      , 
    NUM_ROLE_DEPARTMENT   : ROLE_DEPARTMENT  , 
    NUM_ROLE_DEP_HIST     : ROLE_DEP_HIST    , 
    NUM_ROLE_POST         : ROLE_POST        , 
    NUM_ROLE_EMPLOYEE     : ROLE_EMPLOYEE    , 
    NUM_ROLE_FIO_HIST     : ROLE_FIO_HIST    , 
    NUM_ROLE_CHILD        : ROLE_CHILDREN    , 
    NUM_ROLE_APPOINTMENT  : ROLE_APPOINTMENT , 
    NUM_ROLE_EDUCATION    : ROLE_EDUCATION   , 
    NUM_ROLE_EMPL_PER     : ROLE_EMPLOYEE_PERIOD, 
    NUM_ROLE_PAY_TITLE    : ROLE_PAY_TITLE   , 
    NUM_ROLE_PAYMENT      : ROLE_PAYMENT     , 
    NUM_ROLE_PHOTO        : ROLE_PHOTO       , 
    NUM_ROLE_ACCOUNT      : ROLE_ACCOUNT     , 
}

ROLE_ICON = {
    ROLE_TODO: 'check2-square',
    ROLE_NOTE: 'sticky',
    ROLE_NEWS: 'newspaper',
    ROLE_STORE: 'key',
    ROLE_DOC: 'file-text',
    ROLE_WARR: 'award',
    ROLE_PROJECT: 'kanban',
    ROLE_EXPENSES: 'piggy-bank',
    ROLE_PERSON: 'person',
    ROLE_TRIP: 'truck',
    ROLE_SALDO: 'currency-dollar',
    ROLE_FUEL: 'droplet',
    ROLE_PART: 'cart',
    ROLE_SERVICE: 'tools',
    ROLE_APART: 'building',
    ROLE_METER: 'speedometer2',
    ROLE_PRICE: 'tag',
    ROLE_BILL: 'receipt',
    ROLE_MARKER: 'heart',
    ROLE_INCIDENT: 'termometer-half',
    ROLE_ANAMNESIS: 'info-square',
    ROLE_PERIOD: 'calendar-range',
    ROLE_DEPARTMENT: 'door-closed',
    ROLE_DEP_HIST: 'clock-history',
    ROLE_POST: 'display',
    ROLE_EMPLOYEE: 'people',
    ROLE_FIO_HIST: 'clock-history',
    ROLE_CHILDREN: 'people',
    ROLE_APPOINTMENT: 'briefcase',
    ROLE_EDUCATION: 'book',
    ROLE_EMPLOYEE_PERIOD: 'person-lines-fill',
    ROLE_PAY_TITLE: 'pencil-square',
    ROLE_PAYMENT: 'calculator',
    ROLE_PHOTO: 'image',
    ROLE_ACCOUNT: 'person-check',
}

ROLE_BASE = {
    ROLE_EXPENSES: ROLE_PROJECT,
    ROLE_PERSON: ROLE_TRIP,
    ROLE_SALDO: ROLE_TRIP,
    ROLE_PART: ROLE_FUEL,
    ROLE_SERVICE: ROLE_FUEL,
    ROLE_METER: ROLE_APART,
    ROLE_PRICE: ROLE_APART,
    ROLE_BILL: ROLE_APART,
    ROLE_INCIDENT: ROLE_MARKER,
    ROLE_ANAMNESIS: ROLE_MARKER,
    ROLE_DEPARTMENT: ROLE_PERIOD,
    ROLE_DEP_HIST: ROLE_PERIOD,
    ROLE_POST: ROLE_PERIOD,
    ROLE_EMPLOYEE: ROLE_PERIOD,
    ROLE_FIO_HIST: ROLE_PERIOD,
    ROLE_CHILDREN: ROLE_PERIOD,
    ROLE_APPOINTMENT: ROLE_PERIOD,
    ROLE_EDUCATION: ROLE_PERIOD,
    ROLE_EMPLOYEE_PERIOD: ROLE_PERIOD,
    ROLE_PAY_TITLE: ROLE_PERIOD,
    ROLE_PAYMENT: ROLE_PERIOD,
}

ROLE_APP = {
    ROLE_TODO: APP_TODO,
    ROLE_NOTE: APP_NOTE,
    ROLE_NEWS: APP_NEWS,
    ROLE_STORE: APP_STORE,
    ROLE_DOC: APP_DOCS,
    ROLE_WARR: APP_WARR,
    ROLE_PROJECT: APP_EXPEN,
    ROLE_EXPENSES: APP_EXPEN,
    ROLE_PERSON: APP_EXPEN,
    ROLE_TRIP: APP_TRIP,
    ROLE_SALDO: APP_TRIP,
    ROLE_FUEL: APP_FUEL,
    ROLE_PART: APP_FUEL,
    ROLE_SERVICE: APP_FUEL,
    ROLE_APART: APP_APART,
    ROLE_METER: APP_APART,
    ROLE_PRICE: APP_APART,
    ROLE_BILL: APP_APART,
    ROLE_MARKER: APP_HEALTH,
    ROLE_INCIDENT: APP_HEALTH,
    ROLE_ANAMNESIS: APP_HEALTH,
    ROLE_PERIOD: APP_WORK,
    ROLE_DEPARTMENT: APP_WORK,
    ROLE_DEP_HIST: APP_WORK,
    ROLE_POST: APP_WORK,
    ROLE_EMPLOYEE: APP_WORK,
    ROLE_FIO_HIST: APP_WORK,
    ROLE_CHILDREN: APP_WORK,
    ROLE_APPOINTMENT: APP_WORK,
    ROLE_EDUCATION: APP_WORK,
    ROLE_EMPLOYEE_PERIOD: APP_WORK,
    ROLE_PAY_TITLE: APP_WORK,
    ROLE_PAYMENT: APP_WORK,
    ROLE_PHOTO: APP_PHOTO,
    ROLE_ACCOUNT: APP_HOME,
}