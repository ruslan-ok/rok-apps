from django.contrib.auth.decorators import login_required, permission_required
from apart.v_apart import v_apart_view, v_apart_edit
from apart.v_tarif import do_tarif


#============================================================================
@login_required(login_url='account:login')
@permission_required('apart.view_communal')
#============================================================================
# Представление для отображения списка оплат коммунальных
def bills_view(request, fl):
    return v_apart_view(request, fl)

#============================================================================
@login_required(login_url='account:login')
@permission_required('apart.view_communal')
#============================================================================
# Представление для редактирования записи оплаты коммунальных
def bill_edit(request, fl, per):
    return v_apart_edit(request, fl, per)

#============================================================================
@login_required(login_url='account:login')
@permission_required('apart.view_communal')
#============================================================================
def tariffs_view(request, fl):
    return do_tarif(request, fl, 0)

#============================================================================
@login_required(login_url='account:login')
@permission_required('apart.view_communal')
#============================================================================
def tariff_edit(request, fl, pk):
    return do_tarif(request, fl, pk)


