from django.contrib.auth.decorators import login_required, permission_required
from task.v_task import do_task
from task.v_grps import do_grps
from task.v_view import do_view
from task.v_test import do_test

#============================================================================
@login_required(login_url='account:login')
@permission_required('task.view_task')
def task_view(request):
    return do_task(request, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('task.view_task')
def task_edit(request, pk):
    return do_task(request, pk)


#============================================================================
@login_required(login_url='account:login')
@permission_required('task.view_task')
def grps_view(request):
    return do_grps(request, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('task.view_task')
def grps_edit(request, pk):
    return do_grps(request, pk)

#============================================================================
@login_required(login_url='account:login')
@permission_required('task.view_task')
def view_view(request):
    return do_view(request, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('task.view_task')
def view_edit(request, pk):
    return do_view(request, pk)

#============================================================================
@login_required(login_url='account:login')
@permission_required('task.view_task')
def test_view(request):
    return do_test(request)



