from django.urls import path
from cram.config import app_config
from cram.views import language, training

app_name = app_config['name']
urlpatterns = [
    path('', training.TrainingView.as_view(), name='list'),
    path('lang/', language.LangListView.as_view(), name='lang-list'),
    # path('<int:pk>/', views.DetailView.as_view(), name='item'),
    # path('training/', training.training, name='training'),
    # path('group/<int:pk>/', views.GroupView.as_view(), name='group'),
]
