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
def cars_list(request, folder_id):
    return do_cars(request, folder_id, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для редактирования автомобиля
def cars_form(request, folder_id, content_id):
    return do_cars(request, folder_id, content_id)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для отображения списка заправок
def fuel_list(request, folder_id):
    return do_fuel(request, folder_id, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для редактирования записи заправки
def fuel_form(request, folder_id, content_id):
    return do_fuel(request, folder_id, content_id)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Переключение на другой автомобиль в списке заправок
def change_car(request, folder_id, content_id):
    return do_change_car(request, folder_id, content_id)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для отображения списка расходников
def part_list(request, folder_id):
    return do_part(request, folder_id, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для редактирования расходника
def part_form(request, folder_id, content_id):
    return do_part(request, folder_id, content_id)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для отображения списка замен заданного расходника
def repl_list(request, folder_id, content_id):
    return do_repl(request, folder_id, pt, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('fuel.view_car')
#============================================================================
# Представление для редактирования замены расходника
def repl_form(request, folder_id, pt, content_id):
    return do_repl(request, folder_id, pt, content_id)

