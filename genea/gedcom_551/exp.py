import os
# from genea.models import GenDate, GenTree, GenAlbum, Person, PersBio, PersContact, PersFact, SrcCitation, Family, FamilyFact, FamilyChild, Media
from genea.models import (Header)
from genea.const import *

class ExpGedcom551:
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = request.user

    def export_gedcom_551(self, folder):
        if (not os.path.isdir(folder)):
            return {
                'result': 'error', 
                'folder': folder,
                'description': 'Folder does not exist.',
                }
    """
        for tree in Header.objects.all():
            if self.valid_tree(tree):
                self.exp_tree(folder, tree)
        return {'result': 'ok'}

    def valid_tree(self, tree):
        q1 = (len(GenAlbum.objects.filter(tree=tree)) > 0)
        q2 = (len(Person.objects.filter(tree=tree)) > 0)
        q3 = (len(Family.objects.filter(tree=tree)) > 0)
        q4 = (len(SrcCitation.objects.filter(tree=tree)) > 0)
        return (q1 or q2 or q3 or q4)

    def exp_tree(self, folder, tree):
        fname = 'gen_tree_' + str(tree.id)
        if (tree.mh_id):
            fname = tree.mh_id
        self.f = open(folder + '\\' + fname + '.ged', 'w', encoding='utf-8-sig')
        self.sources = []
        self.write_header(tree)
        for album in GenAlbum.objects.filter(tree=tree):
            self.write_album(album)
        for person in Person.objects.filter(tree=tree):
            self.write_person(person)
        for family in Family.objects.filter(tree=tree):
            self.write_family(family)
        for source in self.sources:
            self.write_source(source)
        self.f.write('0 TRLR\n')
        self.f.close()

    def write_header(self, tree):
        self.f.write('0 HEAD\n')
        self.f.write('1 GEDC\n')
        self.f.write('2 VERS ' + tree.gedcom_vers + '\n')
        self.f.write('2 FORM ' + tree.gedcom_form + '\n')
        self.f.write('1 CHAR UTF-8\n')
        self.f.write('1 LANG ' + tree.language + '\n')
        self.f.write('1 SOUR ' + tree.source + '\n')
        self.f.write('2 NAME ' + tree.src_name + '\n')
        self.f.write('2 VERS ' + tree.src_version + '\n')
        self.f.write('2 _RTLSAVE ' + tree.src_rtl + '\n')
        self.f.write('2 CORP ' + tree.src_corpo + '\n')
        self.f.write('1 DEST ' + tree.destination + '\n')
        self.f.write('1 DATE ' + tree.updated + '\n')
        self.f.write('1 FILE ' + tree.file + '\n')
        self.f.write('1 _PROJECT_GUID ' + tree.prj_id + '\n')
        self.f.write('1 _EXPORTED_FROM_SITE_ID ' + tree.mh_id + '\n')

    # def write_valued_tag(self, level, tag, value):
    #     if value:
    #          self.f.write(str(level) + ' ' + tag + ' ' + value + '\n')

    def write_album(self, item):
        pass

    def write_person(self, item):
        self.f.write('0 @I' + str(item.mh_id) + '@ INDI\n')
        for tag in ():


        self.write_optional(1, '_UPD', item, 'updated')


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
                    self.write_optional(2, 'PLAC', item['immigration'], 'place')
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
                    self.write_optional(2, 'QUAY', item['source'], 'confidence')
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
        pass

    def write_source(self, item):
        pass


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
    """
