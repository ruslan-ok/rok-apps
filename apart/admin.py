from django.contrib import admin
from .models_old import Tarif, Communal
from .models import Apart, Meter, Price, Bill

admin.site.register(Tarif)
admin.site.register(Communal)

admin.site.register(Apart)
admin.site.register(Meter)
admin.site.register(Price)
admin.site.register(Bill)

