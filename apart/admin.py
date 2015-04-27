from django.contrib import admin
from apart.models import Tarif, Communal
from apps.models import Apps

admin.site.register(Apps)
admin.site.register(Tarif)
admin.site.register(Communal)

