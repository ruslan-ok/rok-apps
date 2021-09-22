from django.apps import AppConfig
from news.config import app_config

class NewsConfig(AppConfig):
    name = app_config['name']
