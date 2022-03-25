from rest_framework import viewsets, permissions, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from api.genealogy import GenealogySerializer

WORK_PATH = 'Z:\\apps\\docs\\ruslan.ok\\docs\\Разное\\Хобби\\Генеалогия\\MyHeritage\\2022.0324 export GEDCOM'
GEDCOM_OKUN = 'c3kdnl_590017c686618f23d7nb63_A.ged'
GEDCOM_ZHMA = '129v05_3500205jc3e23q1679zru7_A.ged'
GEDCOM_VOLC = '28ubc9_685758129db6318b1ug97r_A.ged'
GEDCOM_TESL = '134674012_1_DF_d6mg534171c94327.ged'

class GenealogyViewSet(viewsets.ModelViewSet):
    serializer_class = GenealogySerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skip_next_read = False
        self.sort = []

    def get_queryset(self):
        return []

    @action(detail=False)
    def test_gedcom(self, request, pk=None):
        self.res = {}
        # self.read_tree(GEDCOM_OKUN)
        # self.read_tree(GEDCOM_ZHMA)
        self.read_tree(GEDCOM_VOLC)
        # self.read_tree(GEDCOM_TESL)
        self.write_trees()
        return Response(self.res)
    
    def add(self, ged_tag, obj, name, value):
        if (name in obj):
            return
        if ged_tag and (ged_tag not in self.sort):
            self.sort.append(ged_tag)
        obj[name] = value

    def create_append(self, ged_tag, obj, name, value):
        if (name not in obj):
            obj[name] = []
        num = len(obj[name])
        if ged_tag and (ged_tag not in self.sort):
            self.sort.append(ged_tag + '|' + str(num))
        value['sort_number'] = num
        obj[name].append(value)

    def read_tree(self, fname):
        self.f = open(WORK_PATH + '\\' + fname, 'r', encoding='utf-8-sig')
        self.create_append('TREE', self.res, 'trees', self.read_fam_tree())
        self.f.close()

    def next_line(self):
        if self.skip_next_read:
            self.skip_next_read = False
            return
        self.cur_line = self.f.readline()
        if (len(self.cur_line) < 2) or (self.cur_line[1] != ' ') or (self.cur_line[0] not in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
            self.level = None
            self.tag = None
            self.id = None
            self.value = self.cur_line
        else:
            self.level = int(self.cur_line.split(' ')[0])
            tag = self.cur_line.split(' ')[1]
            self.value = ''
            if (len(self.cur_line) > len(str(self.level) + ' ' + tag + ' ')):
                self.value = self.cur_line.split(str(self.level) + ' ' + tag + ' ')[1].replace('\n', '')
            if (tag.find('@') == 0):
                self.tag = tag[1]
                self.id = int(tag.split('@' + self.tag)[1].split('@')[0])
            else:
                self.tag = tag.replace('\n', '')
                self.id = None
        self.skip_next_read = False

    def unexpected_tag(self):
        Exception('Unexpected line: ' + self.cur_line)

    def check_level(self, level):
        if (self.level != level):
            Exception('Unexpected level: ' + str(self.level) + '. Expected is ' + str(level) + '. Current line: ' + self.cur_line)

    def read_fam_tree(self):
        ret = {}
        self.next_line()
        while self.cur_line:
            match (self.level, self.tag):
                case (0, 'HEAD'): ret['header'] = self.read_header()
                case (0, 'A'): self.create_append('A', ret, 'albums', self.read_album())
                case (0, 'I'): self.create_append('I', ret, 'persons', self.read_person())
                case (0, 'F'): self.create_append('F', ret, 'families', self.read_family())
                case (0, 'S'): self.create_append('S', ret, 'sites', self.read_site())
                case (0, 'TRLR'): pass
                case _: self.unexpected_tag()
            self.next_line()
        return ret

    def read_header(self):
        self.check_level(0)
        ret = {}
        self.next_line()
        while self.cur_line and (self.level > 0):
            match (self.level, self.tag):
                case (1, 'GEDC'): ret['gedcom'] = self.read_gedcom()
                case (1, 'CHAR'): ret['encoding'] = self.value
                case (1, 'LANG'): ret['language'] = self.value
                case (1, 'SOUR'): ret['source'] = self.read_header_source()
                case (1, 'DEST'): ret['destination'] = self.value
                case (1, 'DATE'): ret['date'] = self.value
                case (1, 'FILE'): ret['file'] = self.value
                case (1, '_PROJECT_GUID'): ret['project_guid'] = self.value
                case (1, '_EXPORTED_FROM_SITE_ID'): ret['site_id'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_gedcom(self):
        self.check_level(1)
        ret = {}
        self.next_line()
        while self.cur_line and (self.level > 1):
            match (self.level, self.tag):
                case (2, 'VERS'): ret['version'] = self.value
                case (2, 'FORM'): ret['format'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret
        
    def read_header_source(self):
        self.check_level(1)
        ret = {'value': self.value}
        self.next_line()
        while self.cur_line and (self.level > 1):
            match (self.level, self.tag):
                case (2, 'VERS'): ret['version'] = self.value
                case (2, 'NAME'): ret['name'] = self.value
                case (2, '_RTLSAVE'): ret['RTL'] = self.value
                case (2, 'CORP'): ret['corpo'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_site(self):
        self.check_level(0)
        ret = {'site_id': self.id, 'value': self.value}
        self.next_line()
        while self.cur_line and (self.level > 0):
            match (self.level, self.tag):
                case (1, '_UPD'): ret['updated'] = self.value
                case (1, 'AUTH'): ret['author'] = self.value
                case (1, 'TITL'): ret['title'] = self.value
                case (1, 'TEXT'): ret['description'] = self.value
                case (1, '_TYPE'): ret['type'] = self.value
                case (1, '_MEDI'): ret['media_id'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_album(self):
        self.check_level(0)
        if (self.value != 'ALBUM'):
            Exception('For tag A expected value is "ALBUM". Current line: ' + self.cur_line)
        ret = {'album_id': self.id}
        self.next_line()
        while self.cur_line and (self.level > 0):
            match (self.level, self.tag):
                case (1, '_UPD'): ret['updated'] = self.value
                case (1, 'TITL'): ret['title'] = self.value
                case (1, 'DESCRIPTION'): ret['description'] = self.value
                case (1, 'RIN'): ret['RIN'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_person(self):
        self.check_level(0)
        if (self.value != 'INDI'):
            Exception('For tag I expected value is "INDI". Current line: ' + self.cur_line)
        ret = {'person_id': self.id}
        self.sort = []
        self.next_line()
        while self.cur_line and (self.level > 0):
            match (self.level, self.tag):
                case (1, '_UPD'): self.add('_UPD', ret, 'updated', self.value)
                case (1, 'NAME'): self.add('NAME', ret, 'name', self.read_person_name())
                case (1, 'SEX'):  self.add('SEX',  ret, 'sex', self.value)
                case (1, 'DEAT'): self.add('DEAT', ret, 'death', self.read_person_date())
                case (1, 'BURI'): self.add('BURI', ret, 'burial', self.read_person_burial())
                case (1, 'BIRT'): self.add('BIRT', ret, 'birth', self.read_person_date())
                case (1, 'IMMI'): self.add('IMMI', ret, 'imigration', self.read_imigration())
                case (1, 'NATI'): self.add('NATI', ret, 'nationality', self.read_fact())
                case (1, 'DSCR'): self.add('DSCR', ret, 'description', self.value)
                case (1, 'RELI'): self.add('RELI', ret, 'religion', self.value)
                case (1, 'RESI'): self.create_append('RESI', ret, 'contacts', self.read_person_contact())
                case (1, 'EVEN'): self.create_append('PERS_EVEN', ret, 'events', self.read_fact())
                case (1, 'EDUC'): self.create_append('EDUC', ret, 'educations', self.read_fact())
                case (1, 'OCCU'): self.add('OCCU', ret, 'occupation', self.read_fact())
                case (1, 'CHR'): self.add('CHR', ret, 'christening', self.read_fact())
                case (1, 'FAMS'): self.create_append('FAMS', ret, 'families', {'family_id': self.read_link_id('F')})
                case (1, 'FAMC'): self.add('FAMC', ret, 'current_family', self.read_current_family())
                case (1, 'SOUR'): self.add('SOUR', ret, 'source', self.read_source())
                case (1, 'NOTE'): self.add('NOTE', ret, 'notes', self.read_person_notes())
                case (1, 'RIN'):  self.add('RIN',  ret, 'RIN', self.value)
                case (1, 'OBJE'): self.create_append('OBJE', ret, 'objects', self.read_person_object())
                case (1, '_UID'): self.add('_UID', ret, 'UID', self.value)
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        ret['sort_tags'] = self.sort
        return ret

    def read_person_name(self):
        self.check_level(1)
        if self.value:
            ret = {'full': self.value}
        else:
            ret = {}
        self.next_line()
        while self.cur_line and (self.level > 1):
            match (self.level, self.tag):
                case (2, 'GIVN'): ret['first'] = self.value
                case (2, 'SURN'): ret['last'] = self.value
                case (2, '_MARNM'): ret['maiden'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_person_date(self):
        self.check_level(1)
        if self.value:
            ret = {'value': self.value}
        else:
            ret = {}
        self.next_line()
        while self.cur_line and (self.level > 1):
            match (self.level, self.tag):
                case (2, 'DATE'): ret['date'] = self.value
                case (2, 'AGE'): ret['age'] = self.value
                case (2, 'PLAC'): ret['place'] = self.value
                case (2, 'CAUS'): ret['cause'] = self.value
                case (2, 'NOTE'): ret['note'] = self.read_level_notes()
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_imigration(self):
        self.check_level(1)
        if self.value:
            ret = {'value': self.value}
        else:
            ret = {}
        self.next_line()
        while self.cur_line and (self.level > 1):
            match (self.level, self.tag):
                case (2, 'PLAC'): ret['place'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret


    def read_person_burial(self):
        self.check_level(1)
        if self.value:
            ret = {'value': self.value}
        else:
            ret = {}
        self.next_line()
        while self.cur_line and (self.level > 1):
            match (self.level, self.tag):
                case (2, 'DATE'): ret['date'] = self.value
                case (2, 'PLAC'): ret['place'] = self.value
                case (2, 'OBJE'): self.create_append('', ret, 'objects', self.read_burial_object())
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_link_id(self, tag):
        self.check_level(1)
        return int(self.value.split('@' + tag)[1].split('@')[0])

    def read_current_family(self):
        self.check_level(1)
        ret = {'family_id': self.read_link_id('F')}
        self.next_line()
        while self.cur_line and (self.level > 1):
            match (self.level, self.tag):
                case (2, 'PEDI'): ret['adoption'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_person_notes(self):
        self.check_level(1)
        ret = self.value
        self.next_line()
        while self.cur_line and ((self.level == None) or (self.level > 1)):
            match (self.level, self.tag):
                case (2, 'CONC'): ret += self.value
                case (None, None): ret += self.value.replace('\n', '')
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_level_notes(self):
        self.check_level(2)
        ret = self.value
        self.next_line()
        while self.cur_line and ((self.level == None) or (self.level > 2) or ((self.level == 2) and (self.tag == 'NOTE'))):
            match (self.level, self.tag):
                case (2, 'NOTE'): ret += self.value.replace('Witnesses:', ' Witnesses:')
                case (3, 'CONC'): ret += self.value
                case (None, None): ret += self.value.replace('\n', '')
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_person_object(self):
        self.check_level(1)
        ret = {}
        self.next_line()
        while self.cur_line and (self.level > 1):
            match (self.level, self.tag):
                case (2, 'FORM'): ret['format'] = self.value
                case (2, 'FILE'): ret['url'] = self.value
                case (2, '_FILESIZE'): ret['size'] = int(self.value)
                case (2, 'TITL'): ret['title'] = self.value
                case (2, '_DATE'): ret['date'] = self.value
                case (2, '_PLACE'): ret['place'] = self.value
                case (2, '_PRIM'): ret['prim'] = self.value
                case (2, '_CUTOUT'): ret['cutout'] = self.value
                case (2, '_PARENTRIN'): ret['parent_RIN'] = self.value
                case (2, '_PERSONALPHOTO'): ret['personal'] = self.value
                case (2, '_PRIM_CUTOUT'): ret['prim_cutout'] = self.value
                case (2, '_PARENTPHOTO'): ret['parent_photo'] = self.value
                case (2, '_PHOTO_RIN'): ret['RIN'] = self.value
                case (2, '_POSITION'): ret['position'] = self.value.split(' ')
                case (2, '_ALBUM'): ret['album_id'] = self.read_link_id('A')
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_burial_object(self):
        self.check_level(2)
        ret = {}
        self.next_line()
        while self.cur_line and (self.level > 2):
            match (self.level, self.tag):
                case (3, 'FORM'): ret['format'] = self.value
                case (3, 'FILE'): ret['url'] = self.value
                case (3, '_FILESIZE'): ret['size'] = int(self.value)
                case (3, '_DATE'): ret['date'] = self.value
                case (3, '_PHOTO_RIN'): ret['RIN'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_person_contact(self):
        self.check_level(1)
        ret = {}
        self.next_line()
        while self.cur_line and (self.level > 1):
            match (self.level, self.tag):
                case (2, 'EMAIL'): ret['email'] = self.value
                case (2, 'PHON'): ret['phone'] = self.value
                case (2, 'WWW'): ret['web'] = self.value
                case (2, 'ADDR'): ret['address'] = self.read_address()
                case (2, 'NOTE'): ret['note'] = self.read_level_notes()
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_address(self):
        self.check_level(2)
        ret = {}
        self.next_line()
        while self.cur_line and (self.level > 2):
            match (self.level, self.tag):
                case (3, 'ADR1'): ret['address_1'] = self.value
                case (3, 'ADR2'): ret['address_2'] = self.value
                case (3, 'ADR3'): ret['address_3'] = self.value
                case (3, 'CITY'): ret['city'] = self.value
                case (3, 'STAE'): ret['state'] = self.value
                case (3, 'CTRY'): ret['country'] = self.value
                case (3, 'POST'): ret['index'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_family(self):
        self.check_level(0)
        if (self.value != 'FAM'):
            Exception('For tag F expected value is "FAM". Current line: ' + self.cur_line)
        ret = {'family_id': self.id}
        self.next_line()
        self.sort = []
        while self.cur_line and (self.level > 0):
            match (self.level, self.tag):
                case (1, '_UPD'): self.add('_UPD', ret, 'updated', self.value)
                case (1, 'HUSB'): self.add('HUSB', ret, 'husband', self.read_link_id('I'))
                case (1, 'WIFE'): self.add('WIFE', ret, 'wife', self.read_link_id('I'))
                case (1, 'CHIL'): self.create_append('CHIL', ret, 'children', {'child_id': self.read_link_id('I')})
                case (1, 'RIN'):  self.add('RIN', ret, 'RIN', self.value)
                case (1, '_UID'): self.add('_UID', ret, 'UID', self.value)
                case (1, 'MARR'): self.add('MARR', ret, 'marriage', self.read_fact())
                case (1, 'NCHI'): self.add('NCHI', ret, 'NCHI', self.read_fact())
                case (1, 'DIV'):  self.add('DIV', ret, 'divorced', self.read_fact())
                case (1, 'EVEN'): self.create_append('FAM_EVEN', ret, 'events', self.read_fact())
                case (1, 'ENGA'): self.add('ENGA', ret, 'engagement', self.value)
                case (1, 'MARL'): self.add('MARL', ret, 'witnesses', self.read_fact())
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        ret['sort_tags'] = self.sort
        return ret

    def read_source(self):
        self.check_level(1)
        if self.value:
            ret = {'value': self.value}
        else:
            ret = {}
        self.next_line()
        while self.cur_line and (self.level > 1):
            match (self.level, self.tag):
                case (2, 'PAGE'): ret['page'] = self.value
                case (2, 'QUAY'): ret['quantity'] = self.value
                case (2, 'DATA'): ret['data'] = self.read_source_data()
                case (2, 'EVEN'): ret['event'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_source_data(self):
        self.check_level(2)
        ret = {}
        self.next_line()
        while self.cur_line and (self.level > 2):
            match (self.level, self.tag):
                case (3, 'DATE'): ret['date'] = self.value
                case (3, 'TEXT'): ret['text'] = self.value
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def read_fact(self):
        self.check_level(1)
        if self.value:
            ret = {'value': self.value}
        else:
            ret = {}
        self.next_line()
        while self.cur_line and (self.level > 1):
            match (self.level, self.tag):
                case (2, 'TYPE'): ret['type'] = self.value
                case (2, 'DATE'): ret['date'] = self.value
                case (2, 'PLAC'): ret['place'] = self.value
                case (2, 'NOTE'): ret['note'] = self.read_level_notes()
                case _: self.unexpected_tag()
            self.next_line()
        self.skip_next_read = True
        return ret

    def write_trees(self):
        for tree in self.res['trees']:
            fname = tree['header']['site_id']
            self.f = open(WORK_PATH + '\\' + fname + '.ged', 'w', encoding='utf-8-sig')
            self.write_header(tree['header'])
            if ('albums' in tree):
                for album in tree['albums']:
                    self.write_album(album)
            for person in tree['persons']:
                self.write_person(person)
            for family in tree['families']:
                self.write_family(family)
            if ('sites' in tree):
                for site in tree['sites']:
                    self.write_site(site)
            self.f.write('0 TRLR\n')
            self.f.close()

    def write_header(self, header):
        self.f.write('0 HEAD\n')
        self.f.write('1 GEDC\n')
        self.f.write('2 VERS ' + header['gedcom']['version'] + '\n')
        self.f.write('2 FORM ' + header['gedcom']['format'] + '\n')
        self.f.write('1 CHAR ' + header['encoding'] + '\n')
        self.f.write('1 LANG ' + header['language'] + '\n')
        self.f.write('1 SOUR ' + header['source']['value'] + '\n')
        self.f.write('2 NAME ' + header['source']['name'] + '\n')
        self.f.write('2 VERS ' + header['source']['version'] + '\n')
        self.f.write('2 _RTLSAVE ' + header['source']['RTL'] + '\n')
        self.f.write('2 CORP ' + header['source']['corpo'] + '\n')
        self.f.write('1 DEST ' + header['destination'] + '\n')
        self.f.write('1 DATE ' + header['date'] + '\n')
        self.f.write('1 FILE ' + header['file'] + '\n')
        self.f.write('1 _PROJECT_GUID ' + header['project_guid'] + '\n')
        self.f.write('1 _EXPORTED_FROM_SITE_ID ' + header['site_id'] + '\n')

    def write_album(self, item):
        self.f.write('0 @A' + str(item['album_id']) + '@ ALBUM\n')
        self.write_optional(1, 'TITL', item, 'title')
        self.write_optional(1, 'DESCRIPTION', item, 'description')
        self.write_optional(1, '_UPD', item, 'updated')
        self.write_optional(1, 'RIN', item, 'RIN')

    def write_person(self, item):
        self.f.write('0 @I' + str(item['person_id']) + '@ INDI\n')
        for ged_tag in item['sort_tags']:
            if ('|' in ged_tag):
                sub_tag = ged_tag.split('|')[0]
                num = int(ged_tag.split('|')[1])
            else:
                sub_tag = ged_tag
                num = None
            match sub_tag:
                case '_UPD': 
                    self.write_optional(1, '_UPD', item, 'updated')
                case 'NAME': 
                    self.f.write('1 NAME ' + item['name']['full'] + '\n')
                    self.write_optional(2, 'GIVN', item['name'], 'first')
                    self.write_optional(2, 'SURN', item['name'], 'last')
                    self.write_optional(2, '_MARNM', item['name'], 'maiden')
                case 'SEX': 
                    self.write_optional(1, 'SEX', item, 'sex')
                case 'BIRT':
                    self.f.write('1 BIRT\n')
                    self.write_optional(2, 'DATE', item['birth'], 'date')
                    self.write_optional(2, 'PLAC', item['birth'], 'place')
                    self.write_optional(2, 'NOTE', item['birth'], 'note')
                    self.write_optional(2, 'AGE', item['birth'], 'age')
                case 'IMMI':
                    self.f.write('1 IMMI\n')
                    self.write_optional(2, 'PLAC', item['imigration'], 'place')
                case 'DEAT':
                    self.write_optional_value(1, 'DEAT', item['death'], 'value')
                    self.write_optional(2, 'DATE', item['death'], 'date')
                    self.write_optional(2, 'PLAC', item['death'], 'place')
                    self.write_optional(2, 'CAUS', item['death'], 'cause')
                    self.write_optional(2, 'NOTE', item['death'], 'note')
                    self.write_optional(2, 'AGE', item['death'], 'age')
                case 'BURI':
                    self.write_optional_value(1, 'BURI', item['burial'], 'value')
                    self.write_optional(2, 'DATE', item['burial'], 'date')
                    self.write_optional(2, 'PLAC', item['burial'], 'place')
                    if ('objects' in item['burial']):
                        for obj in item['burial']['objects']:
                            self.f.write('2 OBJE\n')
                            self.write_optional(3, 'FORM', obj, 'format')
                            self.write_optional(3, 'FILE', obj, 'url')
                            self.write_optional(3, '_FILESIZE', obj, 'size')
                            self.write_optional(3, '_DATE', obj, 'date')
                            self.write_optional(3, '_PHOTO_RIN', obj, 'RIN')
                case 'NATI': 
                    self.write_fact(1, 'NATI', item['nationality'])
                case 'DSCR': 
                    self.write_optional(1, 'DSCR', item, 'description')
                case 'RELI': 
                    self.write_optional(1, 'RELI', item, 'religion')
                case 'RESI':
                    for contact in item['contacts']:
                        if (contact['sort_number'] != num):
                            continue
                        self.f.write('1 RESI\n')
                        self.write_optional(2, 'EMAIL', contact, 'email')
                        self.write_optional(2, 'PHON', contact, 'phone')
                        self.write_optional(2, 'WWW', contact, 'web')
                        self.write_optional(2, 'NOTE', contact, 'note')
                        if ('address' in contact):
                            self.f.write('2 ADDR\n')
                            self.write_optional(3, 'ADR1', contact['address'], 'address_1')
                            self.write_optional(3, 'ADR2', contact['address'], 'address_2')
                            self.write_optional(3, 'ADR3', contact['address'], 'address_3')
                            self.write_optional(3, 'CITY', contact['address'], 'city')
                            self.write_optional(3, 'STAE', contact['address'], 'state')
                            self.write_optional(3, 'CTRY', contact['address'], 'country')
                            self.write_optional(3, 'POST', contact['address'], 'index')
                case 'PERS_EVEN':
                    for event in item['events']:
                        if (event['sort_number'] != num):
                            continue
                        self.write_fact(1, 'EVEN', event)
                case 'EDUC':
                    for educ in item['educations']:
                        if (educ['sort_number'] != num):
                            continue
                        self.write_fact(1, 'EDUC', educ)
                case 'OCCU':
                    self.write_fact(1, 'OCCU', item['occupation'])
                case 'CHR':
                    self.write_fact(1, 'CHR', item['christening'])
                case 'FAMS':
                    for fam in item['families']:
                        if (fam['sort_number'] != num):
                            continue
                        self.f.write('1 FAMS @F' + str(fam['family_id']) + '@\n')
                case 'FAMC':
                    self.f.write('1 FAMC @F' + str(item['current_family']['family_id']) + '@\n')
                    self.write_optional(2, 'PEDI', item['current_family'], 'adoption')
                case 'SOUR':
                    self.write_optional_value(1, 'SOUR', item['source'], 'value')
                    self.write_optional(2, 'PAGE', item['source'], 'page')
                    self.write_optional(2, 'QUAY', item['source'], 'quantity')
                    self.write_optional_value(2, 'DATA', item['source'], 'x')
                    self.write_optional(3, 'DATE', item['source']['data'], 'date')
                    self.write_optional(3, 'TEXT', item['source']['data'], 'text')
                    self.write_optional(2, 'EVEN', item['source'], 'event')
                case 'NOTE':
                    self.write_optional(1, 'NOTE', item, 'notes')
                case 'RIN':
                    self.write_optional(1, 'RIN', item, 'RIN')
                case '_UID':
                    self.write_optional(1, '_UID', item, 'UID')
                case 'OBJE':
                    for obj in item['objects']:
                        if (obj['sort_number'] != num):
                            continue
                        self.f.write('1 OBJE\n')
                        self.write_optional(2, 'FORM', obj, 'format')
                        self.write_optional(2, 'FILE', obj, 'url')
                        self.write_optional(2, '_FILESIZE', obj, 'size')
                        self.write_optional(2, 'TITL', obj, 'title')
                        self.write_optional(2, '_DATE', obj, 'date')
                        self.write_optional(2, '_PLACE', obj, 'place')
                        self.write_optional(2, '_PRIM', obj, 'prim')
                        self.write_optional(2, '_CUTOUT', obj, 'cutout')
                        self.write_optional(2, '_PARENTRIN', obj, 'parent_RIN')
                        self.write_optional(2, '_PRIM_CUTOUT', obj, 'prim_cutout')
                        self.write_optional(2, '_PERSONALPHOTO', obj, 'personal')
                        self.write_optional(2, '_PARENTPHOTO', obj, 'parent_photo')
                        if ('position' in obj):
                            self.f.write('2 _POSITION ' + ' '.join(obj['position']) + '\n')
                        self.write_link_id(2, '_ALBUM', 'A', None, obj, 'album_id')
                        self.write_optional(2, '_PHOTO_RIN', obj, 'RIN')

    def write_family(self, item):
        self.f.write('0 @F' + str(item['family_id']) + '@ FAM\n')
        for ged_tag in item['sort_tags']:
            if ('|' in ged_tag):
                sub_tag = ged_tag.split('|')[0]
                num = int(ged_tag.split('|')[1])
            else:
                sub_tag = ged_tag
                num = None
            match sub_tag:
                case '_UPD': 
                    self.write_optional(1, '_UPD', item, 'updated')
                case 'HUSB': 
                    self.write_link_id(1, 'HUSB', 'I', None, item, 'husband')
                case 'WIFE': 
                    self.write_link_id(1, 'WIFE', 'I', None, item, 'wife')
                case 'CHIL': 
                    for child in item['children']:
                        if (child['sort_number'] != num):
                            continue
                        self.write_link_id(1, 'CHIL', 'I', child['child_id'])
                case 'RIN': 
                    self.write_optional(1, 'RIN', item, 'RIN')
                case '_UID': 
                    self.write_optional(1, '_UID', item, 'UID')
                case 'MARR': 
                    self.write_fact(1, 'MARR', item['marriage'])
                case 'NCHI': 
                    self.write_fact(1, 'NCHI', item['NCHI'])
                case 'MARL': 
                    self.write_fact(1, 'MARL', item['witnesses'])
                case 'DIV': 
                    self.write_fact(1, 'DIV', item['divorced'])
                case 'EVEN': 
                    for event in item['events']:
                        if (event['sort_number'] != num):
                            continue
                        self.write_fact(1, 'EVEN', event)
                case 'ENGA': 
                    self.write_optional(1, 'ENGA', item, 'engagement')

    def write_site(self, item):
        self.f.write('0 @S' + str(item['site_id']) + '@ SOUR\n')
        self.write_optional(1, '_UPD', item, 'updated')
        self.write_optional(1, 'AUTH', item, 'author')
        self.write_optional(1, 'TITL', item, 'title')
        self.write_optional(1, 'TEXT', item, 'description')
        self.write_optional(1, '_TYPE', item, 'type')
        self.write_optional(1, '_MEDI', item, 'media_id')

    def write_link_id(self, level, ged_tag, liter, id, item={}, tag=''):
        if id or (tag in item):
            if not id:
                id = item[tag]
            self.f.write(str(level) + ' ' + ged_tag + ' @' + liter + str(id) + '@\n')

    def write_fact(self, level, ged_tag, item):
        self.write_optional_value(level, ged_tag, item, 'value')
        self.write_optional(2, 'TYPE', item, 'type')
        self.write_optional(2, 'DATE', item, 'date')
        self.write_optional(2, 'PLAC', item, 'place')
        self.write_optional(2, 'NOTE', item, 'note')

    def write_optional(self, level, ged_tag, item, tag):
        if (tag in item):
            value = ''
            if str(item[tag]):
                value = ' ' + str(item[tag])
            self.f.write(str(level) + ' ' + ged_tag + value + '\n')

    def write_optional_value(self, level, ged_tag, item, tag):
        if (tag in item):
            self.f.write(str(level) + ' ' + ged_tag + ' ' + str(item[tag]) + '\n')
        else:
            self.f.write(str(level) + ' ' + ged_tag + '\n')
