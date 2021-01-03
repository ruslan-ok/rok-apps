from django.urls import path
from . import views

app_name = 'health'
urlpatterns = [
    path('',          views.main,      name = 'main'),
    path('chrono/',   views.chrono,    name = 'chrono'),
    path('biomark/',  views.biomark,   name = 'biomark'),
    path('incident/', views.incident,  name = 'incident'),
    path('<int:pk>/', views.item_form, name = 'item_form'),
]
