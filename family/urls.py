from django.urls import path
from family.config import app_config
from family.views import base, pedigree, diagram, individual, family, media, repo, note, source, submitter, report, calendar

app_name = app_config['name']
urlpatterns = [
    path('', pedigree.PedigreeListView.as_view(), name='list'),
    path('<int:pk>/', pedigree.PedigreeDetailsView.as_view(), name='pedigree-detail'),
    path('<int:ft>/diagram/', diagram.diagram, name='diagram'),
    path('<int:ft>/individual/', individual.IndiListView.as_view(), name='individual-list'),
    path('<int:ft>/individual/<int:pk>/', individual.IndiDetailsView.as_view(), name='individual-detail'),
    path('<int:ft>/individual/<int:pk>/<str:view>', individual.IndiDetailsView.as_view(), name='individual-view'),
    path('<int:ft>/individual/<int:pk>/avatar/', base.avatar, name='avatar'),
    path('<int:ft>/family/', family.FamListView.as_view(), name='family-list'),
    path('<int:ft>/family/<int:pk>/', family.FamDetailsView.as_view(), name='family-detail'),
    path('<int:ft>/media/', media.MediaListView.as_view(), name='media-list'),
    path('<int:ft>/media/<int:pk>/', media.MediaDetailsView.as_view(), name='media-detail'),
    path('<int:ft>/repo/', repo.RepoListView.as_view(), name='repo-list'),
    path('<int:ft>/repo/<int:pk>/', repo.RepoDetailsView.as_view(), name='repo-detail'),
    path('<int:ft>/note/', note.NoteListView.as_view(), name='note-list'),
    path('<int:ft>/note/<int:pk>/', note.NoteDetailsView.as_view(), name='note-detail'),
    path('<int:ft>/source/', source.SourceListView.as_view(), name='source-list'),
    path('<int:ft>/source/<int:pk>/', source.SourceDetailsView.as_view(), name='source-detail'),
    path('<int:ft>/submitter/', submitter.SubmitterListView.as_view(), name='submitter-list'),
    path('<int:ft>/submitter/<int:pk>/', submitter.SubmitterDetailsView.as_view(), name='submitter-detail'),

    path('<int:ft>/report/', report.ReportListView.as_view(), name='report'),
    path('<int:ft>/calendar/', calendar.CalendarListView.as_view(), name='calendar'),

    path('<int:ft>/photo/', base.photo, name='photo'),
    path('<int:ft>/thumbnail/', base.thumbnail, name='thumbnail'),
    path('<int:ft>/thumbnail_100/', base.thumbnail_100, name='thumbnail_100'),
]
