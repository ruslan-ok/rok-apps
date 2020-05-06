from django.contrib.auth.decorators import login_required, permission_required
from proj.v_dirs import do_dirs
from proj.v_proj import do_proj, do_change_dir


#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# Представление для отображения списка направлений
def dirs_list(request, folder_id):
    return do_dirs(request, folder_id, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# Представление для редактирования направления
def dirs_form(request, folder_id, content_id):
    return do_dirs(request, folder_id, content_id)

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# Представление для отображения списка операций проекта
def proj_list(request, folder_id):
    return do_proj(request, folder_id, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# Представление для редактирования операции проекта
def proj_form(request, folder_id, content_id):
    return do_proj(request, folder_id, content_id)

#============================================================================
@login_required(login_url='account:login')
@permission_required('proj.view_proj')
#============================================================================
# Переключение на другое направление
def change_dir(request, folder_id, content_id):
    return do_change_dir(request, folder_id, content_id)
