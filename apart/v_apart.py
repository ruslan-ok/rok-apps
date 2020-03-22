from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from datetime import date, datetime, timedelta
from django.forms import ModelForm
from rusel.const import a_months, t_months
from apart.models import Communal, get_per_tarif


debug_text = ''


#============================================================================


class ApartForm(ModelForm):
    class Meta:
        model = Communal
        exclude = ('user', 'penalty', 'prev_per')
    id       = forms.IntegerField(required = False)
    period   = forms.IntegerField(required = False)
    month    = forms.IntegerField(required = True, widget = forms.Select(choices = t_months))
    year     = forms.IntegerField(required = True, widget = forms.NumberInput(attrs = {'size': 10}))
    #state    = forms.ChoiceField(required = False)



#============================================================================
# Является ли последней записью
def isFirst(_user, _period):
  cmnl = Communal.objects.filter(user = _user).order_by('period')[:1]
  if (len(cmnl) > 0):
    if ((_period // 100) == cmnl[0].year) and ((_period % 100) == cmnl[0].month):
      return 1
  return 0

#============================================================================
# Является ли первой записью
def isLast(_user, _period):
  cmnl = Communal.objects.filter(user = _user).order_by('-period')[:1]
  if (len(cmnl) > 0):
    if ((_period // 100) == cmnl[0].year) and ((_period % 100) == cmnl[0].month):
      return 1
  return 0

#============================================================================
# Нет ни одной записи
def isNoAny(_user):
  cmnl = Communal.objects.filter(user = _user)[:1]
  if (len(cmnl) > 0):
    return 0
  return 1

#============================================================================
# Нормализация целого
def correct_int(_a):
    if (_a == None):
      return 0
    else:  
      return _a

#============================================================================
# Сохранение записи
def my_save(_ins, _user, _per, a, _sCounter, _sPay):
    if (_ins):
      try:
        b = Communal.objects.get(user = _user.id, period = a.year * 100 + a.month)
        return u'Такой период уже есть'
      except Communal.DoesNotExist:
        b = Communal(user = _user)
    else:
      b = Communal.objects.get(user = _user.id, period = _per)

    if (b == None):
      return u'Не удалось создать запись'
    else:
      b.month      = a.month
      b.year       = a.year
      b.period     = a.year * 100 + a.month

      b.state      = correct_int(a.state)
      b.dCounter   = datetime.strptime(_sCounter, '%Y-%m-%d')
      b.dPay       = datetime.strptime(_sPay,     '%Y-%m-%d')
      b.el_old     = correct_int(a.el_old)
      b.el_new     = correct_int(a.el_new)
      b.el_pay     = correct_int(a.el_pay)
      b.tv_tar     = correct_int(a.tv_tar)
      b.tv_pay     = correct_int(a.tv_pay)
      b.phone_tar  = correct_int(a.phone_tar)
      b.phone_pay  = correct_int(a.phone_pay)
      b.zhirovka   = correct_int(a.zhirovka)
      b.hot_pay    = correct_int(a.hot_pay)
      b.repair_pay = correct_int(a.repair_pay)
      b.ZKX_pay    = correct_int(a.ZKX_pay)
      b.cold_old   = correct_int(a.cold_old)
      b.cold_new   = correct_int(a.cold_new)
      b.hot_old    = correct_int(a.hot_old)
      b.hot_new    = correct_int(a.hot_new)
      b.water_pay  = correct_int(a.water_pay)
      b.gas_old    = correct_int(a.gas_old)
      b.gas_new    = correct_int(a.gas_new)
      b.gas_pay    = correct_int(a.gas_pay)
      b.penalty    = correct_int(a.penalty)
      b.prev_per   = correct_int(a.prev_per)
      b.course     = correct_int(a.course)
      b.text       = a.text
      b.save()
      return u''

def get_element(_arr, _ndx):
    if (len(_arr) >= (_ndx+1)):
      return _arr[_ndx]
    else:
      return 0


def edit_context(_request, _form, _debug_text, _year, _month, _new):
    el_tar = get_per_tarif(_request.user.id, 1, _year, _month)
    gs_tar = get_per_tarif(_request.user.id, 2, _year, _month)
    wt_tar = get_per_tarif(_request.user.id, 3, _year, _month)
    ws_tar = get_per_tarif(_request.user.id, 4, _year, _month)
    wo_tar = get_per_tarif(_request.user.id, 5, _year, _month)
    if (_new == 1):
      zf = isNoAny(_request.user.id)
      zl = 1
    else:
      zf = isFirst(_request.user.id, (_year * 100 + _month))
      zl =  isLast(_request.user.id, (_year * 100 + _month))
    return { 'form':       _form, 
             'app_text':   u'Приложения', 
             'tarif_text': u'Тарифы', 
             'page_title': u'Коммунальные платежи', 
             'debug_text': 'first = ' + str(zf) + ', last = ' + str(zl), 
             'is_first':   zf, 
             'is_last':    zl,
             'is_new':     _new, 
             's_period':   a_months[_month-1] + ' ' + str(_year),
             'period_num':   _year*100+_month, 
             'state_str': _form.instance.state_str(),
             'el_t1':  el_tar['t1'],
             'el_b1':  el_tar['b1'],
             'el_t2':  el_tar['t2'],
             'el_b2':  el_tar['b2'],
             'el_t3':  el_tar['t3'],
             
             'gs_t1':  gs_tar['t1'],
             'gs_b1':  gs_tar['b1'],
             'gs_t2':  gs_tar['t2'],
             'gs_b2':  gs_tar['b2'],
             'gs_t3':  gs_tar['t3'],
             
             'wt_t1':  wt_tar['t1'],
             'wt_b1':  wt_tar['b1'],
             'wt_t2':  wt_tar['t2'],
             'wt_b2':  wt_tar['b2'],
             'wt_t3':  wt_tar['t3'],
             
             'wk_t1':  ws_tar['t1'] + wo_tar['t1'],
             'wk_b1':  ws_tar['b1'],
             'wk_t2':  ws_tar['t2'] + wo_tar['t2'],
             'wk_b2':  ws_tar['b2'],
             'wk_t3':  ws_tar['t3'] + wo_tar['t3'],
           }

#============================================================================
# Пустая форма для новой записи
def apart_get_new(request):
    cur_per = date.today()
    m1 = cur_per.month
    y1 = cur_per.year
    # Электроэнергия
    _el_old     = 0
    _el_new     = 0
    # Антенна
    _tv_tar     = 0
    # Вода
    _cold_old   = 0
    _cold_new   = 0
    _hot_old    = 0
    _hot_new    = 0
    # Газ
    _gas_old    = 0
    _gas_new    = 0
    # Курс доллара
    _course     = 0

    last = Communal.objects.filter(user = request.user.id).order_by('-period')[:1]
    if (len(last) > 0):
      cur_per = date(day = 1, month = last[0].month, year = last[0].year)
      if (cur_per.month == 12):
        m1 = 1
        y1 = cur_per.year + 1
      else:
        m1 = cur_per.month + 1
        y1 = cur_per.year

      # Электроэнергия
      _el_old     = last[0].el_new
      _el_new     = last[0].el_new + last[0].el_new - last[0].el_old
      # Антенна
      _tv_tar     = last[0].tv_tar
      # Вода
      _cold_old   = last[0].cold_new
      _cold_new   = last[0].cold_new + last[0].cold_new - last[0].cold_old
      _hot_old    = last[0].hot_new
      _hot_new    = last[0].hot_new + last[0].hot_new - last[0].hot_old
      # Газ
      _gas_old    = last[0].gas_new
      _gas_new    = last[0].gas_new + last[0].gas_new - last[0].gas_old
      # Курс доллара
      _course     = last[0].course

    if (m1 == 12):
      m2 = 1
      y2 = y1 + 1
    else:
      m2 = m1 + 1
      y2 = y1
    
    a = Communal(user = request.user, 
                 month = m1, 
                 year = y1, 
                 period = (y1 * 100 + m1), 
                 #dCounter = date(y2, m2, 1), 
                 #dPay = date(y2, m2, 25),
                 state      = 3,
                 # Электроэнергия
                 el_old     = _el_old,
                 el_new     = _el_new,
                 el_pay     = 0,
                 # Антенна
                 tv_tar     = _tv_tar,
                 tv_pay     = 0,
                 # Телефон
                 phone_tar  = 0,
                 phone_pay  = 0,
                 # Жировка
                 zhirovka   = 0,
                 hot_pay    = 0,
                 repair_pay = 0,
                 ZKX_pay    = 0,
                 # Вода
                 cold_old   = _cold_old,
                 cold_new   = _cold_new,
                 hot_old    = _hot_old,
                 hot_new    = _hot_new,
                 water_pay  = 0,
                 # Газ
                 gas_old    = _gas_old,
                 gas_new    = _gas_new,
                 gas_pay    = 0,
                 
                 penalty    = 0,
                 prev_per   = 0,
                 course     = _course,
                 text       = '')
    form = ApartForm(instance = a#, 
                     #initial = {'dCounter': a.dCounter.isoformat(), 
                     #           'dPay':     a.dPay.isoformat()}
                     )
    context = edit_context(request, form, debug_text, y1, m1, 1) 
    return render(request, 'apart/apart_edit.html', context)

#============================================================================
# Отображение конкретной записи
def apart_get_one(request, per, _debug_text):
    try:
      a = Communal.objects.get(user = request.user.id, period = per)
    except Communal.DoesNotExist:
      a = Communal(user = request.user)
      a.text = 'per = ' + str(per) # Коммент
      if (per == 0):
        a.year = date.today().year
        a.month = date.today().month
        a.period = a.year * 100 + a.month
      else:
        a.period = int(per)
        a.year = a.period // 100
        a.month = a.period % 100
      a.save()
    form = ApartForm(instance = a, 
                     initial = {'dCounter': (a.dCounter+timedelta(days=1)).date().isoformat(), 
                                'dPay': (a.dPay+timedelta(days=1)).date().isoformat()})
    context = edit_context(request, form, _debug_text, a.year, a.month, 0) 
    return render(request, 'apart/apart_edit.html', context)

#============================================================================
# Представление для отображения списка оплат коммунальных
def v_apart_view(request):
    aparts = Communal.objects.filter(user = request.user.id).order_by('-period')[:20]
    context = { 'aparts':       aparts, 
                'aparts_count': Communal.objects.filter(user = request.user.id).count,
                'app_text':   u'Приложения', 
                'tarif_text': u'Тарифы', 
                'page_title': u'Коммунальные платежи', 
                'debug_text': ''
              }
    return render(request, 'apart/apart.html', context)

#============================================================================
# Представление для редактирования записи оплаты коммунальных
def v_apart_edit(request, per):
    if (request.method == 'GET') or (per == '0'):
      if (per == '0'):
        # Пустая форма для новой записи
        return apart_get_new(request)
      else:
        # Отображение конкретной записи
        return apart_get_one(request, int(per), 'ok-1')
    else:
      action = request.POST['action']
      if (action == u'Отменить'):
        # Отмена, возвратиться к списку
        return HttpResponseRedirect(reverse('apart:apart_view', args=()))
      else:
        form = ApartForm(request.POST)
        if not form.is_valid():
          # Ошибки в форме, отобразить её снова
          return apart_get_one(request, int(per), unicode(form.errors.as_data()))
        else:
          a = form.save(commit = False)

          if (action == u'Добавить'):
            debug_text = my_save(True, request.user, 0, a, request.POST['dCounter'], request.POST['dPay'])

          if (action == u'Сохранить'):
            debug_text = my_save(False, request.user, per, a, request.POST['dCounter'], request.POST['dPay'])

          if (action == u'Удалить'):
            debug_text = u''
            a = Communal.objects.get(user = request.user.id, period = per)
            a.delete()

          if (debug_text == u''):
            # Успешно сохранено/удалено
            return HttpResponseRedirect(reverse('apart:apart_view', args=()))
          else:
            # Отобразить ошибку
            debug_text = '2'
            context = edit_context(request, form, debug_text, y1, m1, int(request.POST['is_new'])) 
            return render(request, 'apart/apart_edit.html', context)
