from django.apps import AppConfig
from note.config import app_config

class NoteConfig(AppConfig):
    name = app_config['name']
