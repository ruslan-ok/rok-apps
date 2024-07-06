from django.urls import path
from cram.views import index, group, phrases, training

app_name = 'cram'
urlpatterns = [
    path('', index.IndexView.as_view(), name='index'),
    path('group/<int:pk>/', group.GroupView.as_view(), name='group'),
    path('phrases/<int:group>/', phrases.PhrasesView.as_view(), name='phrases'),
    path('phrases/<int:group>/<int:phrase>/', phrases.PhrasesView.as_view(), name='phrases'),
    path('training/<int:group>/<int:phrase>/', training.TrainingView.as_view(), name='training'),
    path('training/<int:group>/start/', training.training_start, name='training_start'),
    path('training/<int:group>/stop/', training.training_stop, name='training_stop'),
    path('phrases/<int:group>/import/', phrases.import_phrases, name='phrases_import'),
]
