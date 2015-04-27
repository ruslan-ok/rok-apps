from django.contrib import admin
from fuel.models import Car, Fuel

class FuelAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['car']}),
        (None, {'fields': ['pub_date']}),
        (None, {'fields': ['odometr']}),
        (None, {'fields': ['volume']}),
        (None, {'fields': ['price']}),
        (None, {'fields': ['comment']}),
    ]


admin.site.register(Car)
admin.site.register(Fuel, FuelAdmin)
