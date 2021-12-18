from django.apps import AppConfig
from photo.config import app_config

class PhotoConfig(AppConfig):
    name = app_config['name']
