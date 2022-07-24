from django.apps import AppConfig
from backup.config import app_config

class BackupConfig(AppConfig):
    name = app_config['name']
