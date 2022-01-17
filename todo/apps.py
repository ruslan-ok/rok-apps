from django.apps import AppConfig
from todo.config import app_config

class TodoConfig(AppConfig):
    name = app_config['name']
