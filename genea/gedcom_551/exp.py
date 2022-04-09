import os
from django.shortcuts import get_object_or_404
from genea.models import (AssociationStructure, Header, IndividualRecord, FamRecord, MultimediaLink, MultimediaRecord, PersonalNamePieces, 
    PersonalNameStructure, SourceRecord, AlbumRecord, ChangeDate, SubmitterRecord, NoteStructure, NamePhoneticVariation, 
    NameRomanizedVariation, SourceCitation, IndividualEventStructure, IndividualAttributeStructure, ChildToFamilyLink, UserReferenceNumber)
from genea.const import *

class ExpGedcom551:
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = request.user

    def export_gedcom_551(self, folder, pk=0):
        if (not os.path.isdir(folder)):
            return {
                'result': 'error', 
                'folder': folder,
                'description': 'Folder does not exist.',
                }
        if pk:
            head = get_object_or_404(Header.objects.filter(id=pk))
            if self.valid_tree(head):
                self.exp_tree(folder, head)
        else:
            for head in Header.objects.all():
                if self.valid_tree(head):
                    self.exp_tree(folder, head)
        return {'result': 'ok'}

    def valid_tree(self, head):
        q1 = (len(IndividualRecord.objects.filter(head=head)) > 0)
        q2 = (len(FamRecord.objects.filter(head=head)) > 0)
        q3 = (len(MultimediaRecord.objects.filter(head=head)) > 0)
        q4 = (len(SourceRecord.objects.filter(head=head)) > 0)
        q5 = (len(AlbumRecord.objects.filter(head=head)) > 0)
        return (q1 or q2 or q3 or q4 or q5)

    def exp_tree(self, folder, head):
        if head.mh_id:
            fname = head.mh_id
        else:
            fname = head.file.replace('.ged', '')
        self.f = open(folder + '\\' + fname + '.ged', 'w', encoding='utf-8-sig')
        self.write_header(head)
        for x in SubmitterRecord.objects.filter(head=head):
            self.submitter_record(x)
        for x in IndividualRecord.objects.filter(head=head):
            self.indi_record(x)
        for x in FamRecord.objects.filter(head=head):
            self.fam_record(x)
        for x in MultimediaRecord.objects.filter(head=head):
            self.media_record(x)
        for x in SourceRecord.objects.filter(head=head):
            self.source_record(x)
        for x in AlbumRecord.objects.filter(head=head):
            self.album_record(x)
        self.f.write('0 TRLR\n')
        self.f.close()

    def write_header(self, head):
        self.f.write('0 HEAD\n')
        self.f.write('1 GEDC\n')
        self.write_line(2, 'VERS', head.gedc_vers)
        self.write_line(2, 'FORM', head.gedc_form)
        self.write_line(1, 'CHAR', head.char)
        self.write_line(1, 'DEST', head.dest)
        self.write_line(1, 'SOUR', head.sour)
        self.write_line(2, 'VERS', head.sour_vers)
        self.write_line(2, 'NAME', head.sour_name)
        self.write_line(2, 'CORP', head.sour_corp)
        self.write_line(2, '_RTLSAVE', head.mh_rtl)
        if (head.subm_id != None):
            self.f.write('1 SUBM @U' + str(head.subm_id) + '@\n')
        self.write_line(1, 'DATE', head.date)
        self.write_line(2, 'TIME', head.time)
        self.write_line(1, 'LANG', head.lang)
        self.write_line(1, 'FILE', head.file)
        self.write_line(1, '_PROJECT_GUID', head.mh_prj_id)
        self.write_line(1, '_EXPORTED_FROM_SITE_ID', head.mh_id)

    def submitter_record(self, subm):
        self.f.write('0 @U' + str(subm.id) + '@ SUBM\n')
        self.write_line(1, '_UID', subm._uid)
        self.write_line(1, 'NAME', subm.name)
        self.write_address(1, subm.addr)
        for x in MultimediaLink.objects.filter(subm=subm.id):
            self.write_media_link(1, x)
        self.write_line(1, 'RIN', subm.rin)
        for x in NoteStructure.objects.filter(subm=subm.id):
            self.write_note(1, x)
        self.write_chan(1, subm.chan)

    def indi_record(self, indi):
        self.f.write('0 @I' + str(indi.id) + '@ INDI\n')
        self.write_line(1, '_UID', indi._uid)
        for x in PersonalNameStructure.objects.filter(indi=indi.id):
            self.write_name(1, x)
        self.write_line(1, 'SEX', indi.sex)
        for x in IndividualEventStructure.objects.filter(indi=indi.id):
            self.write_indi_event(1, x)
        for x in IndividualAttributeStructure.objects.filter(indi=indi.id):
            self.write_indi_attr(1, x)
        for x in ChildToFamilyLink.objects.filter(chil=indi.id):
            self.write_child(1, x.fami)
        for x in FamRecord.objects.filter(husb=indi.id):
            self.write_spouse(1, x)
        for x in FamRecord.objects.filter(wife=indi.id):
            self.write_spouse(1, x)
        for x in AssociationStructure.objects.filter(indi=indi.id):
            self.write_asso_link(1, x)
        for x in UserReferenceNumber.objects.filter(indi=indi.id):
            self.write_refn(1, x)
        self.write_line(1, 'RIN', indi.rin)
        self.write_chan(1, indi.chan)
        for x in NoteStructure.objects.filter(indi=indi.id):
            self.write_note(1, x)
        for x in SourceCitation.objects.filter(indi=indi.id):
            self.write_citate(1, x)
        for x in MultimediaLink.objects.filter(indi=indi.id):
            self.write_media_link(1, x)

    def fam_record(self, x):
        pass

    def media_record(self, x):
        pass

    def source_record(self, x):
        pass

    def album_record(self, x):
        pass

    # ------ Tools --------

    def write_line(self, level, tag, value):
        if value:
            if (type(value) != ChangeDate):
                self.f.write(str(level) + ' ' + tag + ' ' + value.replace('@', '@@') + '\n')
            else:
                date = value.get_date()
                time = value.get_time()
                if date:
                    self.f.write(str(level) + ' DATE ' + date + '\n')
                    if time:
                        self.f.write(str(level+1) + ' TIME ' + time + '\n')

    def write_address(self, level, addr):
        if addr:
            self.f.write(str(level) + ' ADDR\n')
            self.write_line(level+1, 'ADR1', addr.addr_adr1)
            self.write_line(level+1, 'ADR2', addr.addr_adr2)
            self.write_line(level+1, 'ADR3', addr.addr_adr3)
            self.write_line(level+1, 'CITY', addr.addr_city)
            self.write_line(level+1, 'STAE', addr.addr_stae)
            self.write_line(level+1, 'POST', addr.addr_post)
            self.write_line(level+1, 'CTRY', addr.addr_ctry)
            self.write_line(level, 'PHON', addr.phon)
            self.write_line(level, 'PHON', addr.phon2)
            self.write_line(level, 'PHON', addr.phon3)
            self.write_line(level, 'EMAIL', addr.email)
            self.write_line(level, 'EMAIL', addr.email2)
            self.write_line(level, 'EMAIL', addr.email3)
            self.write_line(level, 'FAX', addr.fax)
            self.write_line(level, 'FAX', addr.fax2)
            self.write_line(level, 'FAX', addr.fax3)
            self.write_line(level, 'WWW', addr.www)
            self.write_line(level, 'WWW', addr.www2)
            self.write_line(level, 'WWW', addr.www3)

    def write_place(self, level, plac):
        if plac:
            value = ''
            if plac.name:
                value  = ' ' + plac.name
            self.f.write(str(level) + ' PLAC' + value + '\n')
            for x in NamePhoneticVariation.objects.filter(plac=plac.id):
                self.write_phonetic(level+1, x)
            for x in NameRomanizedVariation.objects.filter(plac=plac.id):
                self.write_romanized(level+1, x)
            if (plac.map_lati or plac.map_long):
                self.f.write(str(level+1) + ' MAP\n')
                self.write_line(level+2, 'LATI', plac.map_lati)
                self.write_line(level+2, 'LONG', plac.map_long)
                for x in NoteStructure.objects.filter(plac=plac.id):
                    self.write_note(level, x)

    def write_note(self, level, note):
        first_note = True
        lines = note.note.split('\n')
        for line in lines:
            first_line = True
            rest = line
            while rest:
                part = rest
                if (len(rest) > 255):
                    pos = rest.rfind(' ')
                    while (pos > 1 and rest[pos-1] == ' '):
                        pos -= 1
                    part = rest[:pos]
                rest = rest[len(part):]
                if first_note:
                    self.f.write(str(level) + ' NOTE ' + part + '\n')
                    first_note = False
                else:
                    if first_line:
                        self.f.write(str(level+1) + ' CONT ' + part + '\n')
                        first_line = False
                    else:
                        self.f.write(str(level+1) + ' CONC ' + part + '\n')

    def write_chan(self, level, chan):
        if chan:
            self.f.write(str(level) + ' CHAN\n')
            self.write_line(level+1, 'DATE', chan.date)
            self.write_line(level+2, 'TIME', chan.time)

    def write_name(self, level, name):
        value = ''
        if name.piec and name.piec.givn:
            value = name.piec.givn
        if name.piec and name.piec.surn:
            if value:
                value += ' '
            value += '/' + name.piec.surn + '/'
        self.f.write(str(level) + ' NAME ' + value + '\n')
        self.write_line(level+1, 'TYPE', name.type)
        self.write_name_pieces(level+1, name.piec)
        for x in NamePhoneticVariation.objects.filter(name=name.id):
            self.write_phonetic(level+1, x)
        for x in NameRomanizedVariation.objects.filter(name=name.id):
            self.write_romanized(level+1, x)

    def write_name_pieces(self, level, piec):
        if piec:
            self.write_line(level, 'NPFX', piec.npfx)
            self.write_line(level, 'GIVN', piec.givn)
            self.write_line(level, 'NICK', piec.nick)
            self.write_line(level, 'SPFX', piec.spfx)
            self.write_line(level, 'SURN', piec.surn)
            self.write_line(level, 'NSFX', piec.nsfx)
            self.write_line(level, 'NPFX', piec.npfx)
            for x in NoteStructure.objects.filter(pnpi=piec.id):
                self.write_note(level, x)
            for x in SourceCitation.objects.filter(pnpi=piec.id):
                self.write_citate(level, x)

    def write_phonetic(self, level, phon):
        self.f.write(str(level) + ' FONE ' + phon.value + '\n')
        self.write_line(level+1, 'TYPE', phon.type)
        self.write_name_pieces(level+1, phon.piec)

    def write_romanized(self, level, roma):
        self.f.write(str(level) + ' ROMN ' + roma.value + '\n')
        self.write_line(level+1, 'TYPE', roma.type)
        self.write_name_pieces(level+1, roma.piec)

    def write_citate(self, level, cita):
        self.f.write(str(level) + ' @S' + str(cita.id) + '@\n')

    def write_indi_event(self, level, even):
        value = ''
        if even.value:
            value  = ' ' + even.value
        self.f.write(str(level) + ' ' + even.tag + value + '\n')
        self.write_event_detail(level+1, even.deta)
        self.write_line(level, 'AGE',  even.age)
        self.write_child(level, even.famc)
        if even.famc:
            self.write_line(level+1, 'ADOP', even.adop)

    def write_indi_attr(self, level, attr):
        value = ''
        if attr.value:
            value  = ' ' + attr.value
        self.f.write(str(level) + ' ' + attr.tag + value + '\n')
        self.write_event_detail(level+1, attr.deta)
        self.write_line(level+1, 'TYPE', attr.type)

    def write_event_detail(self, level, deta):
        if deta:
            self.write_line(level, 'TYPE', deta.type)
            self.write_line(level, 'DATE', deta.date)
            self.write_place(level, deta.plac)
            self.write_address(level, deta.addr)
            self.write_line(level, 'AGNC', deta.agnc)
            self.write_line(level, 'RELI', deta.reli)
            self.write_line(level, 'CAUS', deta.caus)
            for x in NoteStructure.objects.filter(even=deta.id):
                self.write_note(level, x)
            for x in SourceCitation.objects.filter(even=deta.id):
                self.write_citate(level, x)
            for x in MultimediaLink.objects.filter(even=deta.id):
                self.write_media_link(level, x)

    def write_child(self, level, fam):
        if fam:
            self.write_line(level, 'FAMC', '@F' + str(fam.id) + '@')

    def write_spouse(self, level, fam):
        if fam:
            self.write_line(level, 'FAMS', '@F' + str(fam.id) + '@')

    def write_asso_link(self, level, asso):
        self.f.write(str(level) + ' @?' + str(asso.id) + '@\n')
        self.write_line(level+1, 'RELA', asso.asso_rela)
        for x in SourceCitation.objects.filter(asso=asso.id):
            self.write_citate(level+1, x)
        for x in NoteStructure.objects.filter(asso=asso.id):
            self.write_note(level+1, x)

    def write_refn(self, level, refn):
        self.write_line(level, 'REFN', refn.refn)
        self.write_line(level+1, 'TYPE', refn.type)

    def write_media_link(self, level, media):
        if media.obje:
            self.f.write(str(level) + ' OBJE @M' + str(media.obje.id) + '@\n')

"""

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
