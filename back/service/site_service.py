"""Site service interface

The base behavior of the site service.
"""
from datetime import datetime, timedelta


class SiteService():
    template_name = 'logs'

    def __init__(self, service_descr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_descr = service_descr

    def ripe(self):
        return False, False
        
    def process(self):
        return datetime.now() + timedelta(hours=1)

