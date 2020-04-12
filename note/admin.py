from django.contrib import admin
from .models import List, Note, View, Filter, Param

admin.site.register(List)
admin.site.register(Note)
admin.site.register(View)
admin.site.register(Filter)
admin.site.register(Param)

