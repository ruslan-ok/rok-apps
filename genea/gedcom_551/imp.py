import os, glob
from datetime import datetime
from genea.ged4py.parser import GedcomReader
from genea.models import (Header, AddressStructure, IndividualRecord, SubmitterRecord, RepositoryRecord, 
    ChangeDate, NoteStructure, PersonalNameStructure, NamePhoneticVariation, NameRomanizedVariation, 
    PersonalNamePieces, IndividualAttributeStructure, IndividualEventStructure, EventDetail, PlaceStructure, 
    SourceCitation, MultimediaRecord, MultimediaLink, MultimediaFile, FamRecord, ChildToFamilyLink,
    FamilyEventStructure, AlbumRecord, SourceRecord, SourceRecordData, UserReferenceNumber, NoteRecord)
from genea.const import *

COUNTRIES = [
    ('Литва', 'Литва'),
    ('Белоруссия', 'Беларусь'),
    ('Беларусь', 'Беларусь'),
    ('BY', 'Беларусь'),
    ]

CITIES = [
    ('Вільнюс', 'Вильнюс'),
    ('г. Жодина', 'Жодино'),
    ('г.Жодина', 'Жодино'),
    ('Жодино', 'Жодино'),
    ('г. Волковыск', 'Волковыск'),
    ('г.Волковыск', 'Волковыск'),
    ('г.Волковыск.', 'Волковыск'),
    ('г. Минск', 'Минск'),
    ('г.Минск', 'Минск'),
    ('Г Минск', 'Минск'),
    ('Минск', 'Минск'),
    ('Липецкая обл.,с.Боринское', 'Липецкая обл., с.Боринское'),
    ('г. Брест', 'Брест'),
    ]

STREETS = [
    'ул.Дзержинского, д.55', 
    'ул.Якубова, д.66 , к.1, кв.207', 
    ]

POSTS = [
    '220116', 
    '220095', 
    ]



class ImpGedcom551:
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = request.user

    def import_gedcom_551(self, folder):
        if (not os.path.isdir(folder)):
            return {
                'result': 'error', 
                'folder': folder,
                'description': 'Folder does not exist.',
                }
        os.chdir(folder)
        files = glob.glob('*.ged')
        if (len(files) == 0):
            return {
                'result': 'warning', 
                'folder': folder,
                'description': 'There are no GEDCOM files (*.ged) to import.',
                }
        ret = {
            'folder': folder,
            'files': []
        }

        # self.db_del_trees()
        for file in files:
            if (len(Header.objects.filter(file=file)) == 1):
                head = Header.objects.filter(file=file).get()
                head.before_delete()
                head.delete()
            ret['files'].append(self.imp_tree(folder, file))
        # self.db_del_trees()
        return ret

    def db_del_trees(self):
        for tree in Header.objects.all():
            tree.before_delete()
        Header.objects.all().delete()

    def imp_tree(self, folder, file):
        self.result = 'ok'
        self.stat = {}
        with GedcomReader(folder + '\\' + file) as parser:
            for item in parser.records0():
                match item.tag:
                    case 'HEAD':  head = self.read_header(item)
                    case 'FAM':   self.family_record(head, item)
                    case 'INDI':  self.indi_record(head, item)
                    case 'OBJE':  self.media_record(head, item)
                    case 'NOTE':  self.note_record(head, item)
                    case 'REPO':  self.repo_record(head, item)
                    case 'SOUR':  self.source_record(head, item)
                    case 'SUBM':  self.submit_record(head, item)
                    case 'ALBUM': self.album_record(head, item)
                    case 'TRLR': pass
                    case _: self.unexpected_tag(item.tag)
        ret = {
            'result': self.result,
            'file': file,
            'stat': self.stat,
            'header': len(Header.objects.all()),
            }
        if (self.result != 'ok'):
            ret['error'] = self.error_descr
        return ret

    # ------------- Header ---------------

    def read_header(self, item):
        head = Header.objects.create()
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'SOUR': self.header_source(head, x)
                case 'DEST': head.dest = x.value
                case 'DATE': 
                    head.date = x.value
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'TIME': head.time = y.value
                            case _: self.unexpected_tag(y)
                case 'SUBM': head.subm = x.value
                case 'FILE': head.file = x.value
                case 'COPR': head.copr = x.value
                case 'GEDC':
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'VERS': head.gedc_vers = y.value
                            case 'FORM': head.gedc_form = y.value
                            case _: self.unexpected_tag(y)
                case 'VERS': head.gedc_form_vers = x.value
                case 'CHAR': head.char = x.value
                case 'LANG': head.lang = x.value
                case 'NOTE': head.note = x.value
                case '_PROJECT_GUID': head.mh_prj_id = x.value
                case '_EXPORTED_FROM_SITE_ID': head.mh_id = x.value
                case _: self.unexpected_tag(x)
        head.save()
        if (self.result != 'ok'):
            return None
        return head

    def header_source(self, head, item):
        head.sour = item.value
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'VERS': head.sour_vers = x.value
                case 'NAME': head.sour_name = self.get_name(x.value)
                case '_RTLSAVE': head.mh_rtl = x.value
                case 'CORP': head.sour_corp = x.value
                case 'ADDR'|'PHON'|'EMAIL'|'FAX'|'WWW': head.sour_corp_addr = self.address_struct(x, head.sour_corp_addr, 'Header_' + str(head.id))
                case _: self.unexpected_tag(x)
        self.skip_next_read = True

    # ------------- Family ---------------
    def family_record(self, head, item):
        xref = int(item.xref_id.split('@F')[1].split('@')[0])
        family = FamRecord.objects.create(head=head, xref=xref)
        self.stat['family'] = len(FamRecord.objects.filter(head=head))
        for x in item.sub_tags(follow=False):
            match x.tag:
                case '_UPD': family.updated = x.value
                case 'HUSB': family.husband = self.find_person(head, self.link_id(x.value, 'I'))
                case 'WIFE': family.wife = self.find_person(head, self.link_id(x.value, 'I'))
                case 'CHIL': self.family_child(head, family, self.link_id(x.value, 'I'))
                case 'RIN':  family.rin = x.value
                case '_UID': family.uid = x.value
                case 'MARR': self.family_fact(family, x)
                case 'NCHI': self.family_fact(family, x)
                case 'DIV':  self.family_fact(family, x)
                case 'EVEN': self.family_fact(family, x)
                case 'ENGA': self.family_fact(family, x)
                case 'MARL': self.family_fact(family, x)
                case 'OBJE': self.media_link(head, x, fam=family)
                case 'CHAN': family.chan = self.change_date(x, 'FamRecord_' + str(family.id))
                case '_MSTAT': family._mstat = x.value
                case _: self.unexpected_tag(x)
        family.save()

    def family_child(self, head, family, child_id):
        indi = self.find_person(head, child_id)
        if not indi:
            return
        ChildToFamilyLink.objects.create(fami=family, chil=indi)

    def family_fact(self, fam, item):
        even = FamilyEventStructure.objects.create(fam=fam, tag=item.tag, value=item.value)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'DESC': even.desc = x.value
                case _: even.deta = self.event_detail(fam.head, x, even.deta)
        even.save()

    # ------------- Individual ---------------
    def indi_record(self, head, item):
        xref = int(item.xref_id.split('@I')[1].split('@')[0])
        indi = IndividualRecord.objects.create(head=head, xref=xref)
        self.stat['indi'] = len(IndividualRecord.objects.filter(head=head))
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'SEX':  indi.sex = x.value
                case 'RIN':  indi.rin = x.value
                case 'CHAN': indi.chan = self.change_date(x, 'IndividualRecord_' + str(indi.id))
                case '_UPD': indi._upd = x.value
                case '_UID': indi._uid = x.value
                case 'NAME': self.person_name(x, indi)
                case 'ADOP'|'BIRT'|'BAPM'|'BARM'|'BASM'|'BLES'|'BURI'|'CENS'|'CHR'|'CHRA'|'CONF'|'CREM'|'DEAT'|'EMIG'|'FCOM'|'GRAD'|'IMMI'|'NATU'|'ORDN'|'RETI'|'PROB'|'WILL'|'EVEN':
                    self.pers_event(indi, x)
                case 'CAST'|'DSCR'|'EDUC'|'IDNO'|'NATI'|'NCHI'|'NMR'|'OCCU'|'PROP'|'RELI'|'RESI'|'TITL'|'FACT':
                    self.pers_attr(indi, x)
                case 'SOUR': self.source_citat(head, x, indi=indi)
                case 'NOTE': self.note_struct(x, indi=indi)
                case 'OBJE': self.media_link(head, x, indi=indi)
                case 'FAMS': self.spouse_to_family(head, x)
                case 'FAMC': self.child_to_family(head, indi, x)
                case _: self.unexpected_tag(x)
        indi.save()

    def spouse_to_family(self, head, item):
        xref = int(item.value.split('@F')[1].split('@')[0])
        if not FamRecord.objects.filter(head=head, xref=xref).exists():
            FamRecord.objects.create(head=head, xref=xref)

    def child_to_family(self, head, indi, item):
        xref = int(item.value.split('@F')[1].split('@')[0])
        if FamRecord.objects.filter(head=head, xref=xref).exists():
            fam = FamRecord.objects.filter(head=head, xref=xref).get()
        else:
            fam = FamRecord.objects.create(head=head, xref=xref)
        famc = ChildToFamilyLink.objects.create(fami=fam, chil=indi)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'PEDI': 
                    match x.value:
                        case 'adopted': pedi = ADOP_PL
                        case 'birth':   pedi = BIRT_PL
                        case 'foster':  pedi = FOST_PL
                        case _: pedi = UNKN_PL
                    famc.pedi = pedi
                case 'NOTE': self.note_struct(x, famc=famc)
                case _: self.unexpected_tag(x)
        famc.save()

    def person_name(self, item, indi):
        name = PersonalNameStructure.objects.create(indi=indi) #, name=self.get_name(item.value))
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'TYPE': name.type = x.value
                case 'FONE': self.phonetic(x, name=name)
                case 'ROMN': self.romanized(x, name=name)
                case 'NPFX'|'GIVN'|'NICK'|'SPFX'|'SURN'|'NSFX'|'_MARNM': name.piec = self.name_pieces(x, name.piec)
                case 'SOUR': self.source_citat(indi.head, x, pnpi=name)
                case 'NOTE': self.note_struct(x, pnpi=name)
                case _: self.unexpected_tag(x)
        name.save()

    def phonetic(self, item, name=None, plac=None):
        vari = NamePhoneticVariation.objects.create(name=name, plac=plac, value=item.value)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'TYPE': vari.type = x.value
                case 'NPFX'|'GIVN'|'NICK'|'SPFX'|'SURN'|'NSFX'|'_MARNM': vari.piec = self.name_pieces(x, vari.piec)
                case _: self.unexpected_tag(x)
        vari.save()

    def romanized(self, item, name=None, plac=None):
        vari = NameRomanizedVariation.objects.create(name=name, plac=plac, value=item.value)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'TYPE': vari.type = x.value
                case 'NPFX'|'GIVN'|'NICK'|'SPFX'|'SURN'|'NSFX'|'_MARNM': vari.piec = self.name_pieces(x, vari.piec)
                case _: self.unexpected_tag(x)
        vari.save()

    def name_pieces(self, x, piec):
        if not piec:
            piec = PersonalNamePieces.objects.create()
        match x.tag:
            case 'NPFX': piec.npfx = x.value
            case 'GIVN': piec.givn = x.value
            case 'NICK': piec.nick = x.value
            case 'SPFX': piec.spfx = x.value
            case 'SURN': piec.surn = x.value
            case 'NSFX': piec.nsfx = x.value
            case '_MARNM': piec._marnm = x.value
            case _: self.unexpected_tag(x)
        piec.save()
        return piec

    def pers_attr(self, indi, item):
        attr = IndividualAttributeStructure.objects.create(indi=indi, tag=item.tag, value=item.value)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'AGE':  attr.age  = x.value
                case 'TYPE': attr.type = x.value
                case 'DSCR': attr.dscr = x.value
                case _: attr.deta = self.event_detail(indi.head, x, attr.deta)
        attr.save()
        
    def pers_event(self, indi, item):
        even = IndividualEventStructure.objects.create(indi=indi, tag=item.tag, value=item.value)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'FAMC': even.famc = self.find_family(x.value)
                case 'ADOP': even.adop = x.value
                case 'AGE':  even.age  = x.value
                case _: even.deta = self.event_detail(indi.head, x, even.deta)
        even.save()

    # ------------- Media ---------------
    def media_record(self, head, item):
        obje = None
        if item.xref_id and ('@M' in item.xref_id):
            xref = int(item.xref_id.split('@M')[1].split('@')[0])
            if MultimediaRecord.objects.filter(head=head, xref=xref).exists():
                obje = MultimediaRecord.objects.filter(head=head, xref=xref).get()
            else:
                obje = MultimediaRecord.objects.create(head=head, xref=xref)
        if not obje:
            obje = MultimediaRecord.objects.create(head=head)
        self.stat['media'] = len(MultimediaRecord.objects.filter(head=head))
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'FORM': obje.form = x.value
                case 'FILE': self.media_file(x, obje)
                case '_FILESIZE': obje._size = x.value
                case 'TITL': obje.titl = x.value
                case 'REFN': self.user_ref_num(x, obje=obje)
                case 'RIN':  obje.rin = x.value
                case 'NOTE': self.note_struct(x, obje=obje)
                case 'SOUR': self.source_citat(head, x, obje=obje)
                case 'CHAN': obje.chan = self.change_date(x, 'MultimediaRecord_' + str(obje.id))
                case '_DATE': obje._date = x.value
                case '_PLACE': obje._plac = x.value
                case '_PRIM': obje._prim = x.value
                case '_CUTOUT': obje._cuto = x.value
                case '_PARENTRIN': obje._pari = x.value
                case '_PERSONALPHOTO': obje._pers = x.value
                case '_PRIM_CUTOUT': obje._prcu = x.value
                case '_PARENTPHOTO': obje._pare = x.value
                case '_PHOTO_RIN': obje._prin = x.value
                case '_POSITION': obje._posi = x.value
                case '_ALBUM': obje._albu = self.link_id(x.value, 'A')
                case '_UID': obje._uid = x.value
                case _: self.unexpected_tag(x)
        obje.save()
        return obje

    def media_file(self, item, obje):
        file = MultimediaFile.objects.create(obje=obje, file=item.value)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'FORM': 
                    file.form = x.value
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'TYPE': file.type = y.value
                            case 'MEDI': file.medi = y.value
                            case _: self.unexpected_tag(y)
                case 'TITL': file.titl = x.value
                case '_FDTE': file._fdte = x.value
                case '_FPLC': file._fplc = x.value
        file.save()
        return file

    def media_link(self, head, item, fam=None, indi=None, sour_2=None, sour=None, subm=None, even=None):
        obje = self.media_record(head, item)
        MultimediaLink.objects.create(obje=obje, fam=fam, indi=indi, sour_2=sour_2, sour=sour, subm=subm, even=even)

    # ------------- Note ---------------
    def note_record(self, head, item):
        note = None
        if item.xref_id and ('@T' in item.xref_id):
            xref = int(item.xref_id.split('@T')[1].split('@')[0])
            if NoteRecord.objects.filter(head=head, xref=xref).exists():
                note = NoteRecord.objects.filter(head=head, xref=xref).get()
            else:
                note = NoteRecord.objects.create(head=head, xref=xref)
        if not note:
            note = NoteRecord.objects.create(head=head)
        self.stat['note'] = len(NoteRecord.objects.filter(head=head))
        for x in item.sub_tags(follow=False):
            match x.tag:
                case _: self.unexpected_tag(x)
        note.save()
        return note

    def note_struct(self, item, mode=0, head=None, fam=None, indi=None, sour_2=None, asso=None, chan=None, famc=None, obje=None, repo=None, sour=None, soda=None, srci=None, subm=None, even=None, obje_2=None, pnpi=None, plac=None):
        note = NoteStructure.objects.create(mode=mode, head=head, fam=fam, indi=indi, sour_2=sour_2, asso=asso, chan=chan, famc=famc, obje=obje, repo=repo, sour=sour, soda=soda, srci=srci, subm=subm, even=even, obje_2=obje_2, pnpi=pnpi, plac=plac)
        text = item.value
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'NOTE': text += x.value
                case 'CONC': text += x.value
                case 'CONT': text += x.value
                case None: text += x.value.replace('\n', '')
                case _: self.unexpected_tag(x)
        note.note = text
        note.save()
        return note

    # ------------- Repo ---------------
    def repo_record(self, head, item):
        xref = int(item.xref_id.split('@R')[1].split('@')[0])
        if RepositoryRecord.objects.filter(head=head, xref=xref).exists():
            repo = RepositoryRecord.objects.filter(head=head, xref=xref).get()
        else:
            repo = RepositoryRecord.objects.create(head=head, xref=xref)
        self.stat['repo'] = len(RepositoryRecord.objects.filter(head=head))
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'NAME': repo.name = x.value
                case 'ADDR'|'PHON'|'EMAIL'|'FAX'|'WWW': repo.addr = self.address_struct(x, repo.addr, 'RepositoryRecord_' + str(repo.id))
                case 'RIN':  repo.rin  = x.value
                case 'CHAN': repo.chan = x.value
                case _: self.unexpected_tag(x)
        repo.save()

    # ------------- Source ---------------
    def source_record(self, head, item):
        xref = int(item.xref_id.split('@S')[1].split('@')[0])
        if SourceRecord.objects.filter(head=head, xref=xref).exists():
            sour = SourceRecord.objects.filter(head=head, xref=xref).get()
        else:
            sour = SourceRecord.objects.create(head=head, xref=xref)
        self.stat['source'] = len(SourceRecord.objects.filter(head=head))
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'DATA': self.source_data(x, sour)
                case 'AUTH': sour.auth = x.value
                case 'TITL': sour.titl = x.value
                case 'ABBR': sour.abbr = x.value
                case 'PUBL': sour.publ = x.value
                case 'TEXT': sour.text = x.value
                case 'REPO': self.source_repo_link(x, sour)
                case 'REFN': self.user_ref_num(x, sour=sour)
                case 'RIN':  sour.rin = x.value
                case 'CHAN': sour.chan = self.change_date(x, 'SourceRecord_' + str(sour.id))
                case 'NOTE': self.note_struct(x, sour=sour)
                case 'OBJE': self.media_link(head, x, sour=sour)
                case '_UPD': sour._upd = x.value
                case '_TYPE': sour._type = x.value
                case '_MEDI': sour._medi = x.value
                case '_UID': sour._uid = x.value
                case _: self.unexpected_tag(x)
        sour.save()

    def source_data(self, item, sour):
        data = SourceRecordData.objects.create(sour=sour)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'EVEN': data.even = x.value
                case 'DATE': data.date = x.value
                case 'PLAC': data.plac = x.value
                case 'AGNC': data.agnc = x.value
                case _: self.unexpected_tag(x)
        data.save()

    def source_repo_link(self, item, sour):
        pass # TODO

    def source_citat(self, head, item, fam=None, indi=None, asso=None, obje=None, even=None, pnpi=None, note=None, ):
        sour = int(item.value.split('@S')[1].split('@')[0])
        cita = SourceCitation.objects.create(sour=sour, fam=fam, indi=indi, asso=asso, obje=obje, even=even, pnpi=pnpi, note=note)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'PAGE': cita.sour_page = x.value
                case 'QUAY': cita.sour_quay = x.value
                case 'EVEN': cita.sour_even = x.value
                case 'ROLE': cita.sour_even_role = x.value
                case 'AUTH': cita.auth = x.value
                case 'TITL': cita.titl = x.value
                case 'DATA': pass
                case 'DATE': cita.sour_data_date = x.value
                case 'TEXT': cita.sour_data_text = x.value
                case 'NOTE': self.note_struct(x, sour_2=cita)
                case 'OBJE': self.media_link(head, x, sour_2=cita)
                case '_UPD': cita._upd = x.value
                case '_TYPE': cita._type = x.value
                case '_MEDI': cita._medi = x.value
                case _: self.unexpected_tag(x)
        cita.save()

    # ------------- Submitter ---------------
    def submit_record(self, head, item):
        if (item.xref_id == '@U@'):
            xref = '0'
        else:
            xref = item.xref_id.split('@U')[1].split('@')[0]
        subm = SubmitterRecord.objects.create(head=head, xref=xref)
        self.stat['submitter'] = len(SubmitterRecord.objects.filter(head=head))
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'NAME': subm.name = self.get_name(x.value)
                case 'ADDR'|'PHON'|'EMAIL'|'FAX'|'WWW': subm.addr = self.address_struct(x, subm.addr, 'SubmitterRecord_' + str(subm.id))
                case 'RIN':  subm.rin  = x.value
                case 'CHAN': subm.chan = self.change_date(x, 'SubmitterRecord_' + str(subm.id))
                case '_UID': subm._uid = x.value
                case _: self.unexpected_tag(x)
        subm.save()

    # ------------- Album ---------------
    def album_record(self, head, item):
        xref = int(item.xref_id.split('@A')[1].split('@')[0])
        album = AlbumRecord.objects.create(head=head, xref=xref)
        self.stat['album'] = len(AlbumRecord.objects.filter(head=head))
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'TITL': album.titl = x.value
                case 'DESCRIPTION': album.desc = x.value
                case '_UPD': album._upd = x.value
                case 'RIN':  album.rin  = x.value
                case _: self.unexpected_tag(x)
        album.save()

    # ------------- Tools ---------------
    def address_struct(self, x, addr, owner):
        if not addr:
            addr = AddressStructure.objects.create(owner=owner)
        value = ''
        match x.tag:
            case 'ADDR':
                if x.value:
                    value = x.value
                for y in x.sub_tags(follow=False):
                    match y.tag:
                        case 'CONT': value += '\n' + y.value
                        case 'ADR1': addr.addr_adr1 = y.value
                        case 'ADR2': addr.addr_adr2 = y.value
                        case 'ADR3': addr.addr_adr3 = y.value
                        case 'CITY': addr.addr_city = y.value
                        case 'STAE': addr.addr_stae = y.value
                        case 'CTRY': addr.addr_ctry = y.value
                        case 'POST': addr.addr_post = y.value
            case 'PHON':
                if not addr.phon:
                    addr.phon = x.value
                elif not addr.phon2:
                    addr.phon2 = x.value
                else:
                    addr.phon3 = x.value
            case 'EMAIL':
                if not addr.email:
                    addr.email = x.value.replace('@@', '@')
                elif not addr.email2:
                    addr.email2 = x.value.replace('@@', '@')
                else:
                    addr.email3 = x.value.replace('@@', '@')
            case 'FAX':
                if not addr.fax:
                    addr.fax = x.value
                elif not addr.fax2:
                    addr.fax2 = x.value
                else:
                    addr.fax3 = x.value
            case 'WWW':
                if not addr.www:
                    addr.www = x.value
                elif not addr.www2:
                    addr.www2 = x.value
                else:
                    addr.www3 = x.value
            case _: self.unexpected_tag(x)
        if value:
            for ctry in COUNTRIES:
                value = self.check_addr_ctry(addr, value, ctry)
            for city in CITIES:
                value = self.check_addr_city(addr, value, city)
            for street in STREETS:
                value = self.check_addr_street(addr, value, street)
            for post in POSTS:
                value = self.check_addr_post(addr, value, post)

        addr.save()
        return addr

    def check_addr_ctry(self, addr, addr_value, value):
        if (value[0] in addr_value and not addr.addr_ctry):
            addr.addr_ctry = value[1]
            addr_value.replace(value[0], '')
        return addr_value

    def check_addr_city(self, addr, addr_value, value):
        if (value[0] in addr_value and not addr.addr_city):
            addr.addr_city = value[1]
            addr_value.replace(value[0], '')
        return addr_value

    def check_addr_street(self, addr, addr_value, value):
        if (value in addr_value and not addr.addr_adr1):
            addr.addr_adr1 = value
            addr_value.replace(value, '')
        return addr_value

    def check_addr_post(self, addr, addr_value, value):
        if (value in addr_value and not addr.addr_post):
            addr.addr_post = value
            addr_value.replace(value, '')
        return addr_value

    def place_struct(self, item):
        plac = PlaceStructure.objects.create(name=item.value)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'FONE': self.phonetic(x, plac=plac)
                case 'ROMN': self.romanized(x, plac=plac)
                case 'MAP':  pass
                case 'LATI': plac.map_lati = x.value
                case 'LONG': plac.map_long = x.value
                case _: self.unexpected_tag(x)
        plac.save()
        return plac
        
    def change_date(self, item, owner):
        chan = ChangeDate.objects.create(owner=owner)
        if item.value:
            chan.date = str(item.value)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'DATE': 
                    chan.date = str(x.value)
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'TIME': chan.time = str(y.value)
                            case _: self.unexpected_tag(y)
                case 'NOTE': self.note_struct(x, chan=chan)
                case _: self.unexpected_tag(x)
        try:
            chan.date = datetime.strptime(chan.date + ' ' + chan.time, '%d/%m/%y %H:%M:%S')
        except:
            pass
        chan.save()
        return chan

    def event_detail(self, head, x, deta):
        if not deta:
            deta = EventDetail.objects.create()
        match x.tag:
            case 'TYPE': deta.type = x.value
            case 'AGE':  deta.age  = x.value
            case 'DATE': deta.date = x.value
            case 'PLAC': deta.plac = self.place_struct(x)
            case 'ADDR'|'PHON'|'EMAIL'|'FAX'|'WWW': deta.addr = self.address_struct(x, deta.addr, 'EventDetail_' + str(deta.id))
            case 'AGNC': deta.agnc = x.value
            case 'RELI': deta.reli = x.value
            case 'CAUS': deta.caus = x.value
            case 'SOUR': self.source_citat(head, x, even=deta)
            case 'NOTE': self.note_struct(x, even=deta)
            case 'OBJE': self.media_link(head, x, even=deta)
            case _: self.unexpected_tag(x)
        deta.save()
        return deta

    def find_person(self, head, xref):
        if IndividualRecord.objects.filter(head=head, xref=xref).exists():
            return IndividualRecord.objects.filter(head=head, xref=xref)[0]
        return None

    def find_pers_by_id(self, head, person_id):
        if IndividualRecord.objects.filter(head=head, id=person_id).exists():
            return IndividualRecord.objects.filter(head=head, id=person_id).get()
        return None

    def find_family(self, head, xref):
        xref_id = int(xref.split('@F')[1].split('@')[0])
        if FamRecord.objects.filter(head=head, xref=xref_id).exists():
            return FamRecord.objects.filter(head=head, xref=xref_id)[0]
        return None

    def link_id(self, value, tag):
        return int(value.split('@' + tag)[1].split('@')[0])

    def user_ref_num(self, item, indi=None, obje=None, note=None, repo=None, sour=None):
        refn = UserReferenceNumber.objects.create(refn=item.value, indi=indi, obje=obje, note=note, repo=repo, sour=sour)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'TYPE': refn.type = x.value
                case _: self.unexpected_tag(x)
        refn.save()


    def raise_error(self, descr):
        self.result = 'error'
        # self.error_line = self.cur_line.replace('\n', '')
        self.error_descr = descr
        # self.cur_line = None
        raise Exception(descr)

    def unexpected_tag(self, item):
        ret = str(item.offset) + ', tag: ' + item. tag
        if item.xref_id:
            ret += ', xref_id: ' + item.xref_id
        if item.value:
            ret += ', value: ' + item.value
        self.raise_error('Unexpected tag. Offset: ' + ret)

    def get_name(self, value):
        if (type(value) == tuple) and (len(value) == 3) and (value[1] == '') and (value[2] == ''):
            return value[0]
        else:
            return value


    """
    def pers_description(self, person):
        person.height = self.get_tag('HEIGHT')
        person.weight = self.get_tag('WEIGHT')
        person.hair_color = self.get_tag('HAIR')
        person.eye_color = self.get_tag('EYES')

    def spec_pers_attr(self, person, category, type, value):
        if (not category):
            if (type == 'Hobbies'):
                person.interests = value
            elif (type == 'Activities'):
                person.activities = value
            elif (type == 'Favorite music'):
                person.music = value
            elif (type == 'Favorite movies'):
                person.movies = value
            elif (type == 'Favorite TV shows'):
                person.tv_shows = value
            elif (type == 'Favorite books'):
                person.books = value
            elif (type == 'Sports'):
                person.sports = value
            elif (type == 'Favorite restaurants'):
                person.restaurants = value
            elif (type == 'Favorite food'):
                person.cuisines = value
            elif (type == 'Idols'):
                person.people = value
            elif (type == 'Vacation spots'):
                person.getaways = value
            elif (type == 'Favorite quotes'):
                person.quotes = value
            elif (type == 'Language spoken'):
                person.lang_spoken = value
            elif (type == 'Political view'):
                person.political_views = value
            else:
                return False
            person.save()
            return True
        return False

    def get_tag(self, attr):
        if (attr in x.value):
            return x.value.split('<' + attr + '>')[1].split('</' + attr + '>')[0]
        return None
    """

