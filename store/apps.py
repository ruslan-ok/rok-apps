from django.apps import AppConfig
from store.config import app_config

class StoreConfig(AppConfig):
    name = app_config['name']
