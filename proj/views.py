from django.contrib.auth.decorators import login_required, permission_required
from proj.v_dirs import do_dirs
from proj.v_proj import do_proj, do_change_dir


#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# Представление для отображения списка направлений
def dirs_view(request):
    return do_dirs(request, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# Представление для редактирования направления
def dirs_edit(request, pk):
    return do_dirs(request, int(pk))

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# Представление для отображения списка операций проекта
def proj_view(request):
    return do_proj(request, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# Представление для редактирования операции проекта
def proj_edit(request, pk):
    return do_proj(request, int(pk))

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# Переключение на другое направление
def change_dir(request, pk):
    return do_change_dir(request, int(pk))
