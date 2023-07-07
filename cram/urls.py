from django.urls import path
from cram.config import app_config
from cram.views import index, language, phrase, training, group
#from cram.views import cram, group

app_name = app_config['name']
urlpatterns = [
    path('', index.IndexView.as_view(), name='list'),
    path('lang/', language.LangListView.as_view(), name='lang-list'),
    path('lang/<slug:lng>/', language.LangDetailView.as_view(), name='lang-item'),
    path('phrase/<int:grp>/', phrase.PhraseListView.as_view(), name='phrase-list'),
    path('phrase/<int:grp>/<int:pk>/<str:lng>/', phrase.PhraseDetailView.as_view(), name='phrase-item'),
    path('training/<int:grp>/<int:pk>/<str:lng>/', training.TrainingView.as_view(), name='training'),
    path('group/<int:pk>/', group.GroupView.as_view(), name='group'),
]
