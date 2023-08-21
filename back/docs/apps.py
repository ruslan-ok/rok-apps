from django.apps import AppConfig
from docs.config import app_config

class DocsConfig(AppConfig):
    name = app_config['name']
