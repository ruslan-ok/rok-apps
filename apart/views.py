# coding=UTF-8
from django.contrib.auth.decorators import login_required
from apart.v_apart import v_apart_view, v_apart_edit
from apart.v_tarif import do_tarif


#============================================================================
@login_required
#============================================================================
# Представление для отображения списка оплат коммунальных
def apart_view(request):
    return v_apart_view(request)

#============================================================================
@login_required
#============================================================================
# Представление для редактирования записи оплаты коммунальных
def apart_edit(request, per):
    return v_apart_edit(request, per)

#============================================================================
@login_required
#============================================================================
def tarif_view(request):
    return do_tarif(request, 0)

#============================================================================
@login_required
#============================================================================
def tarif_edit(request, pk):
    return do_tarif(request, pk)


