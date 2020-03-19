from django.contrib.auth.decorators import login_required
from fuel.v_cars import do_cars
from fuel.v_fuel import do_fuel, do_change_car
from fuel.v_part import do_part
from fuel.v_repl import do_repl
from django.shortcuts import render


def hello(request):
    return render(request, 'hello.html')



#============================================================================
# Представление для отображения списка автомобилей/редактирования автомобиля
@login_required(login_url='account:login')
def cars(request, pk=0):
    return do_cars(request, pk)

#============================================================================
@login_required(login_url='account:login')
def index(request):
    return do_fuel(request, 0)

#============================================================================
@login_required(login_url='account:login')
#============================================================================
# Представление для редактирования записи заправки
def fuel_edit(request, pk):
    return do_fuel(request, int(pk))

#============================================================================
@login_required(login_url='account:login')
#============================================================================
# Переключение на другой автомобиль в списке заправок
def change_car(request, pk):
    return do_change_car(request, int(pk))

#============================================================================
@login_required(login_url='account:login')
#============================================================================
# Представление для отображения списка расходников
def part_view(request):
    return do_part(request, 0)

#============================================================================
@login_required(login_url='account:login')
#============================================================================
# Представление для редактирования расходника
def part_edit(request, pk):
    return do_part(request, int(pk))

#============================================================================
@login_required(login_url='account:login')
#============================================================================
# Представление для отображения списка замен заданного расходника
def repl_view(request, pt):
    return do_repl(request, int(pt), 0)

#============================================================================
@login_required(login_url='account:login')
#============================================================================
# Представление для редактирования замены расходника
def repl_edit(request, pt, pk):
    return do_repl(request, int(pt), int(pk))

