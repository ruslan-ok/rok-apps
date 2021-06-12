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

ROLE_TODO             = 'todo'            
ROLE_NOTE             = 'note'            
ROLE_NEWS             = 'news'            
ROLE_STORE            = 'store'           
ROLE_DOC              = 'doc'             
ROLE_WARR             = 'warr'            
ROLE_EXPEN            = 'expen'           
ROLE_EXPEN_SALDO      = 'expen_saldo'     
ROLE_TRIP_PERS        = 'trip_pers'       
ROLE_TRIP             = 'trip'            
ROLE_TRIP_SALDO       = 'trip_saldo'      
ROLE_FUEL             = 'fuel'            
ROLE_FUEL_PART        = 'fuel_part'       
ROLE_FUEL_SERV        = 'fuel_serv'       
ROLE_APART_SERV       = 'apart_serv'      
ROLE_APART_METER      = 'apart_meter'     
ROLE_APART_PRICE      = 'apart_price'     
ROLE_APART_BILL       = 'apart_bill'      
ROLE_HEALTH_MARKER    = 'health_marker'   
ROLE_HEALTH_INCIDENT  = 'health_incident' 
ROLE_HEALTH_ANAMNESIS = 'health_anamnesis'
ROLE_WORK_PERIOD      = 'work_period'     
ROLE_WORK_DEPART      = 'work_depart'     
ROLE_WORK_DEP_HIST    = 'work_dep_hist'   
ROLE_WORK_POST        = 'work_post'       
ROLE_WORK_EMPL        = 'work_empl'       
ROLE_WORK_FIO_HIST    = 'work_fio_hist'   
ROLE_WORK_CHILD       = 'work_child'      
ROLE_WORK_APPOINT     = 'work_appoint'    
ROLE_WORK_EDUCAT      = 'work_educat'     
ROLE_WORK_EMPL_PER    = 'work_empl_per'   
ROLE_WORK_PAY_TITLE   = 'work_pay_title'  
ROLE_WORK_PAYMENT     = 'work_payment'    
ROLE_PHOTO            = 'photo'           

ALL_ROLES = (
             ROLE_TODO,             
             ROLE_NOTE,             
             ROLE_NEWS,             
             ROLE_STORE,            
             ROLE_DOC,              
             ROLE_WARR,             
             ROLE_EXPEN,            
             ROLE_EXPEN_SALDO,
             ROLE_TRIP_PERS,        
             ROLE_TRIP,             
             ROLE_TRIP_SALDO,       
             ROLE_FUEL,             
             ROLE_FUEL_PART,
             ROLE_FUEL_SERV,        
             ROLE_APART_SERV,       
             ROLE_APART_METER,      
             ROLE_APART_PRICE,      
             ROLE_APART_BILL,       
             ROLE_HEALTH_MARKER,    
             ROLE_HEALTH_INCIDENT,  
             ROLE_HEALTH_ANAMNESIS, 
             ROLE_WORK_PERIOD,      
             ROLE_WORK_DEPART,      
             ROLE_WORK_DEP_HIST,    
             ROLE_WORK_POST,        
             ROLE_WORK_EMPL,        
             ROLE_WORK_FIO_HIST,    
             ROLE_WORK_CHILD,       
             ROLE_WORK_APPOINT,     
             ROLE_WORK_EDUCAT,      
             ROLE_WORK_EMPL_PER,    
             ROLE_WORK_PAY_TITLE,   
             ROLE_WORK_PAYMENT,     
             ROLE_PHOTO,            
            )

"""
There are Available Roles for each Application
"""
TASK_ROLE_CHOICE   = [(NONE, '--------'), (TASK, _('task'))]
NOTE_ROLE_CHOICE   = [(NONE, '--------'), (NOTE, _('note'))]
NEWS_ROLE_CHOICE   = [(NONE, '--------'), (NEWS, _('news'))] 
STORE_ROLE_CHOICE  = [(NONE, '--------'), (STORE, _('store'))]
DOC_ROLE_CHOICE    = [(NONE, '--------'), (DOC, _('doc'))]
WARR_ROLE_CHOICE   = [(NONE, '--------'), (WARR, _('warranty'))]
EXPEN_ROLE_CHOICE  = [(NONE, '--------'), (OPERATION, _('operation')), (SALDO, _('saldo'))]
TRIP_ROLE_CHOICE   = [(NONE, '--------'), (PERSON, _('person')), (TRIP, _('trip')), (SALDO, _('saldo'))]
FUEL_ROLE_CHOICE   = [(NONE, '--------'), (FUEL, _('fueling')), (PART, _('car part service interval')), (SERVICE, _('service'))]
APART_ROLE_CHOICE  = [(NONE, '--------'), (NONE, '--------'), (SERVICE, _('service')), (METER, _('meter')), (PRICE, _('price')), (BILL, _('bill'))]
HEALTH_ROLE_CHOICE = [(NONE, '--------'), (MARKER, _('marker')), (INCIDENT, _('incident')), (ANAMNESIS, _('anamnesis'))]
WORK_ROLE_CHOICE   = [(NONE, '--------'), (PERIOD, _('period')), (DEPARTMENT, _('department')), (DEP_HIST, _('department history')), 
                      (POST, _('post')), (EMPLOYEE, _('employee')), (FIO_HIST, _('surname history')), (CHILD, _('child')), 
                      (APPOINTMENT, _('appointment')), (EDUCATION, _('education')), (EMPL_PER, _('periods for employee')),
                      (PAY_TITLE, _('pay tytle')), (PAYMENT, _('payment'))]
PHOTO_ROLE_CHOICE  = [(NONE, '--------'), (PHOTO, _('photo'))]

