from django.db.models import Q
from v2_hier.search import SearchResult
from wage.models import app_name, Depart, Post, Employee, FioHist, Child, Appoint, Education, PayTitle, Payment
from .views import DEP_LIST, POST, TITLE, EMPL_LIST, SUR, CHLD, APP, EDUC, PAY


def search(user, query):
    result = SearchResult(query)
    
    lookups = Q(name__icontains=query) | Q(sort__icontains=query)
    items = Depart.objects.filter(user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, DEP_LIST, item.id, item.created(), item.name, item.sort, False)

    lookups = Q(name__icontains=query)
    items = Post.objects.filter(user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, POST, item.id, None, item.name, '', False)

    lookups = Q(name__icontains=query)
    items = PayTitle.objects.filter(user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, TITLE, item.id, None, item.name, '', False)

    lookups = Q(fio__icontains=query) | Q(login__icontains=query) | Q(sort__icontains=query) | Q(email__icontains=query) | Q(passw__icontains=query) | Q(phone__icontains=query) | Q(addr__icontains=query) | Q(info__icontains=query)
    items = Employee.objects.filter(user = user.id).filter(lookups)
    for item in items:
        #todo: Show all fields
        result.add(app_name, EMPL_LIST, item.id, item.born, item.name(), item.info, False)

    lookups = Q(fio__icontains=query) | Q(info__icontains=query)
    items = FioHist.objects.filter(employee__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, SUR, item.id, item.dEnd, str(item), None, item.info, False, item.employee.fio)

    lookups = Q(name__icontains=query) | Q(sort__icontains=query) | Q(info__icontains=query)
    items = Child.objects.filter(employee__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, CHLD, item.id, item.born, str(item), item.info, False, item.employee.fio)

    lookups = Q(tabnum__icontains=query) | Q(info__icontains=query)
    items = Appoint.objects.filter(employee__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, APP, item.id, item.dBeg, item.name(), item.info, False, item.employee.fio)

    lookups = Q(institution__icontains=query) | Q(course__icontains=query) | Q(specialty__icontains=query) | Q(qualification__icontains=query) | Q(document__icontains=query) | Q(number__icontains=query) | Q(city__icontains=query) | Q(info__icontains=query)
    items = Education.objects.filter(employee__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, EDUC, item.id, item.dBeg, item.name(), item.info, False, item.employee.fio)

    lookups = Q(sort__icontains=query) | Q(info__icontains=query)
    items = Payment.objects.filter(employee__user = user.id).filter(lookups)
    for item in items:
        result.add(app_name, PAY, item.id, item.payed, item.name(), item.info, False, item.employee.fio, item.period.name())

    return result.items
