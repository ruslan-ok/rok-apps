from django.contrib.auth.decorators import login_required, permission_required
from fuel.v_cars import do_cars
from fuel.v_fuel import do_fuel, do_change_car
from fuel.v_part import do_part
from fuel.v_repl import do_repl


#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для отображения списка автомобилей
def cars_view(request, fl):
    return do_cars(request, fl, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для редактирования автомобиля
def cars_edit(request, fl, pk):
    return do_cars(request, fl, pk)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для отображения списка заправок
def fuel_list(request, fl):
    return do_fuel(request, fl, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для редактирования записи заправки
def fuel_edit(request, fl, pk):
    return do_fuel(request, fl, pk)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Переключение на другой автомобиль в списке заправок
def change_car(request, fl, pk):
    return do_change_car(request, fl, pk)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для отображения списка расходников
def part_view(request, fl):
    return do_part(request, fl, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для редактирования расходника
def part_edit(request, fl, pk):
    return do_part(request, fl, pk)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для отображения списка замен заданного расходника
def repl_view(request, fl, pt):
    return do_repl(request, fl, pt, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для редактирования замены расходника
def repl_edit(request, fl, pt, pk):
    return do_repl(request, fl, pt, pk)

