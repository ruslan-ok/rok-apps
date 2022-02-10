from django.utils.translation import gettext_lazy as _, gettext
from .utils import get_main_menu_item, APPS

ENTITIES = {
    'apart':     ('apart',       'apartment'),
    'meter':     ('meters data', 'execute'),
    'bill':      ('bill',        'cost'),
    'service':   ('service',     'key'),
    'price':     ('tariff',      'application'),
    'cars':      ('car',         'car'),
    'fuel':      ('fueling',     'gas'),
    'interval':  ('spare part',  'part'),
    'service':   ('replacement', 'key'),
    'note':      ('note',        '/'),
    'news':      ('news',        '/'),
    'project':   ('project',     'work'),
    'expense':   ('expense',     'cost'),
    'entry':     ('password',    'key'),
    'person':    ('person',      'user'),
    'trip':      ('trip',        'car'),
    'department':('department',  'application'),
    'post':      ('post',        'application'),
    'pay_title': ('pay title',   'application'),
    'employee':  ('employee',    'user'),
    'surname':   ('surname change history', 'application'),
    'child':     ('child',       'user'),
    'appoint':   ('appointment', 'application'),
    'education': ('education',   'application'),
    'payment':   ('payment',     'cost'),
    'task':      ('task',        'application'),
    'group':     ('group',       '/'),
    'list':      ('list',        '/'),
}

class SearchResult():
    def __init__(self, query):
        self.query = query
        self.items = []
        
    def add(self, app, entity, id, created, name, info, main_entity = True, detail1 = '', detail2 = ''):
        prefix = ''
        if (not info):
            info = ''
        if (len(info) > 500):
            pos = info.find(self.query)
            if (pos > 250):
                pos -= 250
                prefix = '... '
            else:
                pos = 0
            info = prefix + info[pos:pos+500] + ' ...'
        self.items.append(SearchItem(app, entity, id, created, name, info.replace(self.query, '<strong>' + self.query + '</strong>'), main_entity, detail1, detail2))
        
class SearchItem():
    def __init__(self, app, entity, id, created, name, info, main_entity = True, detail1 = '', detail2 = ''):
        self.app = app
        self.entity = entity
        self.main = main_entity
        self.id = id
        self.created = created
        self.name = name
        self.info = info
        self.detail1 = detail1
        self.detail2 = detail2
        
    def __repr__(self):
        return 'Application: "{}", Entity: "{}", Created: "{}", Name: "{}" , Info: "{}"'.format(self.app, self.entity, self.created, self.name, self.info)

    def href(self):
        pass

    def app_name(self):
        return get_main_menu_item(self.app)

    def app_icon(self):
        return 'v2/rok/icon/' + APPS[self.app][0] + '.png'

    def ent_icon(self):
        if self.entity in ENTITIES:
            icon_name = ENTITIES[self.entity][1]
            if (icon_name == '/'):
                icon_name = self.entity
            return 'v2/rok/icon/' + icon_name + '.png'
        return 'v2/rok/icon/inline/separator.png'

    def ent_name(self):
        if self.entity in ENTITIES:
            return _(ENTITIES[self.entity][0]).capitalize()
        return self.entity


