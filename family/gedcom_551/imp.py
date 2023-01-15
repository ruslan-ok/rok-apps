import os, glob
from datetime import datetime
from family.ged4py.parser import GedcomReader
from family.models import (FamTree, AddressStructure, IndividualRecord, SubmitterRecord, RepositoryRecord, 
    ChangeDate, NoteStructure, PersonalNameStructure, NamePhoneticVariation, NameRomanizedVariation, 
    PersonalNamePieces, IndividualAttributeStructure, IndividualEventStructure, EventDetail, PlaceStructure, 
    SourceCitation, MultimediaRecord, MultimediaLink, MultimediaFile, FamRecord, ChildToFamilyLink,
    FamilyEventStructure, AlbumRecord, SourceRecord, UserReferenceNumber, NoteRecord, SourceRepositoryCitation,
    AssociationStructure, FamTreePermission, FamTreeUser)
from family.const import *

class ImpGedcom551:
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = request.user
        self.only_clear = False

    def import_gedcom_551(self, path):
        if self.only_clear:
            qnt = self.db_del_trees()
            return {'result': 'ok', 'number of deleted trees': qnt,}

        if (not os.path.exists(path)):
            return {
                'result': 'error', 
                'path': path,
                'description': 'The specified path does not exist.',
                }
        folder = None
        file = None
        if os.path.isdir(path):
            folder = path
        else:
            file = os.path.basename(path)

        if folder:
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
                'time': None,
                'files': []
            }

            start = datetime.now()

            for file in files:
                if (len(FamTree.objects.filter(file=file)) == 1):
                    tree = FamTree.objects.filter(file=file).get()
                    tree.before_delete()
                    tree.delete()
                filepath = folder + '\\' + file
                ret['files'].append(self.imp_tree(filepath))

            ret['time'] = datetime.now() - start
        elif file:
            start = datetime.now()

            if (len(FamTree.objects.filter(file=file)) == 1):
                tree = FamTree.objects.filter(file=file).get()
                tree.before_delete()
                tree.delete()
            ret = self.imp_tree(path)

            ret['time'] = datetime.now() - start
        else:
            ret = {
                'result': 'error',
                'path': path,
                'description': 'Unknown error.',
            }

        return ret

    def db_del_trees(self):
        qnt = 0
        for tree in FamTree.objects.all():
            tree.before_delete()
            qnt += 1
        FamTree.objects.all().delete()
        return qnt

    def imp_tree(self, filepath):
        self.result = 'ok'
        self.stat = {}
        self.head_subm = 0
        self.tree = None
        with GedcomReader(filepath) as parser:
            for item in parser.records0():
                match item.tag:
                    case 'HEAD':  self.read_header(item, os.path.basename(filepath))
                    case 'FAM':   self.family_record(item)
                    case 'INDI':  self.indi_record(item)
                    case 'OBJE':  self.media_record(item)
                    case 'NOTE':  self.note_record(item)
                    case 'REPO':  self.repo_record(item)
                    case 'SOUR':  self.source_record(item)
                    case 'SUBM':  self.submit_record(item)
                    case 'ALBUM'|'_ALBUM': self.album_record(item)
                    case 'TRLR': pass
                    case _: self.unexpected_tag(item.tag)

        self.stat['family'] = len(FamRecord.objects.filter(tree=self.tree))
        self.stat['indi'] = len(IndividualRecord.objects.filter(tree=self.tree))
        self.stat['media'] = len(MultimediaRecord.objects.filter(tree=self.tree))
        self.stat['note'] = len(NoteRecord.objects.filter(tree=self.tree))
        self.stat['repo'] = len(RepositoryRecord.objects.filter(tree=self.tree))
        self.stat['source'] = len(SourceRecord.objects.filter(tree=self.tree))
        self.stat['submitter'] = len(SubmitterRecord.objects.filter(tree=self.tree))
        self.stat['album'] = len(AlbumRecord.objects.filter(tree=self.tree))

        if self.result == 'ok':
            FamTreePermission.objects.create(user=self.user, tree=self.tree, can_view=True, can_clone=True, can_change=False, can_delete=True, can_merge=False)

        ret = {
            'result': self.result,
            'file': os.path.basename(filepath),
            'tree_id': self.tree.id,
            'stat': self.stat,
            'header': len(FamTree.objects.all()),
            }
        if (self.result != 'ok'):
            ret['error'] = self.error_descr
        return ret

    # ------------- FamTree ---------------

    def read_header(self, item, file):
        name = file.replace('.ged', '').replace('.GED', '')
        num = 0
        ft = FamTreeUser.objects.filter(user_id=self.user.id)
        for t in ft:
            if t.name and t.name.startswith(name):
                tail = t.name.replace(name, '').replace('(', '').replace(')', '')
                if not tail:
                    if num == 0:
                        num = 1
                else:
                    try:
                        tmp = int(tail)
                        if tmp >= num:
                            num = tmp + 1 
                    except Exception:
                        pass
        if num > 0:
            name = f'{name} ({num})'

        tree = FamTree.objects.create(depth=0, name=name)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'SOUR': self.header_source(tree, x)
                case 'DEST': tree.dest = x.value
                case 'DATE': 
                    tree.date = x.value
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'TIME': tree.time = y.value
                            case _: self.unexpected_tag(y)
                case 'SUBM':
                    s_id = self.extract_xref(x.tag, x.value)
                    if s_id:
                        self.head_subm = int(s_id)
                case 'FILE': tree.file = file
                case 'COPR': tree.copr = x.value
                case 'GEDC':
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'VERS': tree.gedc_vers = y.value
                            case 'FORM': tree.gedc_form = y.value
                            case _: self.unexpected_tag(y)
                case 'CHAR': 
                    tree.char = x.value
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'VERS': tree.char_vers = y.value
                            case _: self.unexpected_tag(y)
                case 'LANG': tree.lang = x.value
                case 'NOTE': 
                    tree.note = x.value
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'CONC': tree.note += y.value
                            case 'CONT': tree.note += '\n' + y.value
                            case _: self.unexpected_tag(y)
                case '_PROJECT_GUID': tree.mh_prj_id = x.value
                case '_EXPORTED_FROM_SITE_ID': tree.mh_id = x.value
                case _: self.unexpected_tag(x)
        tree.save()
        if (self.result != 'ok'):
            return None
        self.tree = tree

    def header_source(self, tree, item):
        tree.sour = item.value
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'VERS': tree.sour_vers = x.value
                case 'NAME': tree.sour_name = self.get_name(x.value)
                case '_RTLSAVE': tree.mh_rtl = x.value
                case '_TREE': tree.name = x.value
                case 'CORP': 
                    tree.sour_corp = x.value
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'ADDR'|'PHON'|'EMAIL'|'FAX'|'WWW': 
                                tree.sour_corp_addr = self.address_struct(y, tree.sour_corp_addr, 'Header_' + str(tree.id))
                            case _: self.unexpected_tag(x)
                case 'DATA': 
                    tree.sour_data = x.value
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'DATE': tree.sour_data_date = y.value
                            case 'COPR': 
                                copr = y.value
                                for z in y.sub_tags(follow=False):
                                    match z.tag:
                                        case 'CONC': text += z.value
                                        case 'CONT': text += '\n' + z.value
                                        case _: self.unexpected_tag(z)
                                tree.sour_data_copr = copr
                            case _: self.unexpected_tag(y)
                case _: self.unexpected_tag(x)
        self.skip_next_read = True

    # ------------- Family ---------------
    def family_record(self, item):
        xref = self.extract_xref(item.tag, item.xref_id)
        sort = len(FamRecord.objects.filter(tree=self.tree).exclude(_sort=None)) + 1
        if FamRecord.objects.filter(tree=self.tree, xref=xref).exists():
            fam = FamRecord.objects.filter(tree=self.tree, xref=xref).get()
            if (not fam._sort):
                fam._sort = sort
                fam.save()
        else:
            fam = FamRecord.objects.create(tree=self.tree, xref=xref, _sort=sort)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'MARR'|'DIV'|'EVEN'|'ENGA'|'MARL'|'NCHI': self.family_fact(fam, x)
                case 'HUSB': fam.husb = self.find_person(self.extract_xref('INDI', x.value))
                case 'WIFE': fam.wife = self.find_person(self.extract_xref('INDI', x.value))
                case 'CHIL': self.family_child(fam, self.extract_xref('INDI', x.value))
                case 'REFN': self.user_ref_num(x, fam=fam)
                case 'RIN':  fam.rin = x.value
                case 'CHAN': fam.chan = self.change_date(x, 'FamRecord_' + str(fam.id))
                case 'NOTE': self.note_struct(x, fam=fam)
                case 'SOUR': self.source_citat(x, fam=fam)
                case 'OBJE': self.media_link(x, fam=fam)
                case '_UID': fam._uid = x.value
                case '_UPD': fam._upd = x.value
                case '_MSTAT': fam._mstat = x.value
                case _: self.unexpected_tag(x)
        fam.save()

    def family_child(self, fam, child_id):
        indi = self.find_person(child_id)
        if not indi:
            return
        if not ChildToFamilyLink.objects.filter(fami=fam, chil=indi).exists():
            ChildToFamilyLink.objects.create(fami=fam, chil=indi, _sort=indi._sort)

    def family_fact(self, fam, item):
        sort = len(FamilyEventStructure.objects.filter(fam=fam)) + 1
        even = FamilyEventStructure.objects.create(fam=fam, tag=item.tag, value=item.value, _sort=sort)
        age = None
        empty = True
        for x in item.sub_tags(follow=False):
            empty = False
            match x.tag:
                case 'DESC': even.desc = x.value
                case _: even.deta, age = self.event_detail(x, even.deta)
        if item.tag == 'HUSB' and not even.husb_age and age:
            even.husb_age = age
        if item.tag == 'WIFE' and not even.wife_age and age:
            even.wife_age = age
        if item.tag == 'MARR' and not even.value and empty:
            even.value = 'Y'
        if item.tag in ('ANUL', 'CENS', 'DIV', 'DIVF',) and (even.value == 'Y'):
            even.value = ''
        even.save()

    # ------------- Individual ---------------
    def indi_record(self, item):
        xref = self.extract_xref(item.tag, item.xref_id)
        sort = len(IndividualRecord.objects.filter(tree=self.tree)) + 1
        indi = IndividualRecord.objects.create(tree=self.tree, xref=xref, _sort=sort)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'NAME': self.person_name(x, indi)
                case 'SEX':  indi.sex = x.value
                case 'ADOP'|'BIRT'|'BAPM'|'BARM'|'BASM'|'BLES'|'BURI'|'CENS'|'CHR'|'CHRA'|'CONF'|'CREM'|'DEAT'|'EMIG'|'FCOM'|'GRAD'|'IMMI'|'NATU'|'ORDN'|'RETI'|'PROB'|'WILL'|'EVEN':
                    self.pers_event(indi, x)
                case 'CAST'|'DSCR'|'EDUC'|'IDNO'|'NATI'|'NCHI'|'NMR'|'OCCU'|'PROP'|'RELI'|'RESI'|'TITL'|'FACT':
                    self.pers_attr(indi, x)
                case 'FAMC': self.child_to_family(indi, x)
                case 'FAMS': self.spouse_to_family(x)
                case 'ASSO': self.association_struct(indi, x)
                case 'REFN': self.user_ref_num(x, indi=indi)
                case 'RIN':  indi.rin = x.value
                case 'CHAN': indi.chan = self.change_date(x, 'IndividualRecord_' + str(indi.id))
                case 'NOTE': self.note_struct(x, indi=indi)
                case 'SOUR': self.source_citat(x, indi=indi)
                case 'OBJE': self.media_link(x, indi=indi)
                case '_UPD': indi._upd = x.value
                case '_UID': indi._uid = x.value
                case _: self.unexpected_tag(x)
        indi.save()

    def spouse_to_family(self, item):
        xref = self.extract_xref('FAM', item.value)
        if not FamRecord.objects.filter(tree=self.tree, xref=xref).exists():
            FamRecord.objects.create(tree=self.tree, xref=xref)

    def child_to_family(self, indi, item):
        xref = self.extract_xref('FAM', item.value)
        if FamRecord.objects.filter(tree=self.tree, xref=xref).exists():
            fam = FamRecord.objects.filter(tree=self.tree, xref=xref).get()
        else:
            fam = FamRecord.objects.create(tree=self.tree, xref=xref)
        if ChildToFamilyLink.objects.filter(fami=fam, chil=indi).exists():
            famc = ChildToFamilyLink.objects.filter(fami=fam, chil=indi).get()
        else:
            famc = ChildToFamilyLink.objects.create(fami=fam, chil=indi, _sort=indi._sort)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'PEDI': famc.pedi = x.value
                case 'NOTE': self.note_struct(x, famc=famc)
                case _: self.unexpected_tag(x)
        famc.save()

    def person_name(self, item, indi):
        sort = len(PersonalNameStructure.objects.filter(indi=indi)) + 1
        name = PersonalNameStructure.objects.create(indi=indi, _sort=sort, name=item.value)
        empty = True
        for x in item.sub_tags(follow=False):
            empty = False
            match x.tag:
                case 'TYPE': name.type = x.value
                case 'FONE': self.phonetic(x, name=name)
                case 'ROMN': self.romanized(x, name=name)
                case 'NPFX'|'GIVN'|'NICK'|'SPFX'|'SURN'|'NSFX'|'_MARNM': name.piec = self.name_pieces(x, name.piec)
                case 'SOUR': self.source_citat(x, pnpi=name)
                case 'NOTE': self.note_struct(x, pnpi=name)
                case _: self.unexpected_tag(x)
        if empty:
            name.delete()
        else:
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
        sort = len(IndividualAttributeStructure.objects.filter(indi=indi)) + 1
        attr = IndividualAttributeStructure.objects.create(indi=indi, tag=item.tag, value=item.value, _sort=sort)
        age = None
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'AGE':  attr.age  = x.value
                case 'TYPE': attr.type = x.value
                case 'DSCR': attr.dscr = x.value
                case _: attr.deta, age = self.event_detail(x, attr.deta)
        if not attr.age and age:
            attr.age = age
        if (attr.tag == 'EDUC') and (not attr.value) and attr.deta and NoteStructure.objects.filter(even=attr.deta).exists():
            note = NoteStructure.objects.filter(even=attr.deta).get()
            if note.note and note.note.note and (len(note.note.note) <= 248):
                attr.value = note.note.note
                note.note.delete()
                note.delete()
        attr.save()
        
    def pers_event(self, indi, item):
        sort = len(IndividualEventStructure.objects.filter(indi=indi)) + 1
        even = IndividualEventStructure.objects.create(indi=indi, tag=item.tag, value=item.value, _sort=sort)
        age = None
        empty = True
        for x in item.sub_tags(follow=False):
            empty = False
            match x.tag:
                case 'FAMC': even.famc = self.find_family(x.value)
                case 'ADOP': even.adop = x.value
                case 'AGE':  even.age  = x.value
                case _: even.deta, age = self.event_detail(x, even.deta)
        if not even.age and age:
            even.age = age
        if (even.tag == 'DEAT') and empty and (not even.value):
            even.value = 'Y'
        if (even.tag == 'DEAT') and (not empty) and (even.value == 'Y'):
            even.value = ''
        if (even.tag in ('BURI', 'CREM', 'ADOP', 'BAPM', 'BARM', 'BASM', 'BLES', 'CHRA', 'CONF', 'FCOM', 'ORDN', 'NATU', 'EMIG', 'IMMI', 'CENS', 'PROB', 'WILL', 'GRAD', 'RETI')) \
            and even.value:
            self.note_struct_for_value(even.value, even=even.deta)
            even.value = ''
        even.save()
        if (even.tag == 'BIRT') and empty:
            even.delete()


    def association_struct(self, indi, item):
        xref = self.extract_xref('INDI', item.value)
        link = self.find_person(xref)
        sort = len(AssociationStructure.objects.filter(indi=indi)) + 1
        asso = AssociationStructure.objects.create(indi=indi, asso=link, _sort=sort)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'RELA': asso.rela = x.value
                case 'SOUR': self.source_citat(x, asso=asso)
                case 'NOTE': self.note_struct(x, asso=asso)
                case _: self.unexpected_tag(x)
        asso.save()

    # ------------- Media ---------------
    def media_record(self, item, xref=None):
        if not xref:
            xref = self.extract_xref(item.tag, item.xref_id)
        if MultimediaRecord.objects.filter(tree=self.tree, xref=xref).exists():
            obje = MultimediaRecord.objects.filter(tree=self.tree, xref=xref).get()
        else:
            sort = len(MultimediaRecord.objects.filter(tree=self.tree)) + 1
            obje = MultimediaRecord.objects.create(tree=self.tree, xref=xref, _sort=sort)
        file = None
        form = ''
        titl = ''
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'FILE': file = self.media_file(x, obje)
                case 'FORM': form = x.value
                case 'TITL': titl = x.value.strip()
                case 'REFN': self.user_ref_num(x, obje=obje)
                case 'RIN':  obje.rin = x.value
                case 'NOTE': self.note_struct(x, obje=obje)
                case 'SOUR': self.source_citat(x, obje=obje)
                case 'CHAN': obje.chan = self.change_date(x, 'MultimediaRecord_' + str(obje.id))
                case '_FILESIZE': obje._size = x.value
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
                case '_ALBUM': 
                    xref = self.extract_xref('_ALBUM', x.value)
                    obje._albu = self.album_record(x, xref)
                case '_UID': obje._uid = x.value
                case _: self.unexpected_tag(x)
        obje.save()
        #  5.5 structure, implemented in MyHeritage
        if file and (form or titl):
            file.form = form
            file.titl = titl
            file.save()
        return obje

    def media_file(self, item, obje):
        sort = len(MultimediaFile.objects.filter(obje=obje)) + 1
        file = MultimediaFile.objects.create(obje=obje, file=item.value, _sort=sort)
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

    def media_link(self, item, fam=None, indi=None, cita=None, sour=None, subm=None, even=None):
        if item.value:
            xref = self.extract_xref('OBJE', item.value)
        else:
            xref = len(MultimediaRecord.objects.filter(tree=self.tree)) + 1
        obje = self.media_record(item, xref)
        sort = len(MultimediaLink.objects.filter(obje=obje, fam=fam, indi=indi, cita=cita, sour=sour, subm=subm, even=even)) + 1
        MultimediaLink.objects.create(obje=obje, fam=fam, indi=indi, cita=cita, sour=sour, subm=subm, even=even, _sort=sort)
        
    # ------------- Note ---------------
    def note_record(self, item, xref=None, value=None):
        if not xref:
            if not value and item.xref_id:
                xref = self.extract_xref(item.tag, item.xref_id)
            else:
                xref = len(NoteRecord.objects.filter(tree=self.tree)) + 1
        if NoteRecord.objects.filter(tree=self.tree, xref=xref).exists():
            note = NoteRecord.objects.filter(tree=self.tree, xref=xref).get()
        else:
            sort = len(NoteRecord.objects.filter(tree=self.tree)) + 1
            note = NoteRecord.objects.create(tree=self.tree, xref=xref, _sort=sort)
        if value:
            text = value
        else:
            text = item.value
            for x in item.sub_tags(follow=False):
                match x.tag:
                    case 'NOTE': text += x.value
                    case 'CONC': text += x.value
                    case 'CONT': text += '\n' + x.value
                    case None: text += x.value.replace('\n', '')
                    case _: self.unexpected_tag(x)
        note.note = text
        note.save()
        return note

    def note_struct(self, item, mode=0, fam=None, indi=None, cita=None, asso=None, chan=None, famc=None, obje=None, repo=None, sour=None, srci=None, subm=None, even=None, pnpi=None, plac=None):
        xref = self.extract_xref('NOTE', item.value)
        note = self.note_record(item, xref=xref)
        sort = len(NoteStructure.objects.filter(mode=mode, tree=self.tree, fam=fam, indi=indi, cita=cita, asso=asso, chan=chan, famc=famc, obje=obje, repo=repo, sour=sour, srci=srci, subm=subm, even=even, pnpi=pnpi, plac=plac)) + 1
        note_stru = NoteStructure.objects.create(mode=mode, tree=self.tree, note=note, fam=fam, indi=indi, cita=cita, asso=asso, chan=chan, famc=famc, obje=obje, repo=repo, sour=sour, srci=srci, subm=subm, even=even, pnpi=pnpi, plac=plac, _sort=sort)
        return note_stru

    def note_struct_for_value(self, value, mode=0, fam=None, indi=None, cita=None, asso=None, chan=None, famc=None, obje=None, repo=None, sour=None, srci=None, subm=None, even=None, pnpi=None, plac=None):
        note = self.note_record(None, value=value)
        sort = len(NoteStructure.objects.filter(mode=mode, tree=self.tree, fam=fam, indi=indi, cita=cita, asso=asso, chan=chan, famc=famc, obje=obje, repo=repo, sour=sour, srci=srci, subm=subm, even=even, pnpi=pnpi, plac=plac)) + 1
        note_stru = NoteStructure.objects.create(mode=mode, tree=self.tree, note=note, fam=fam, indi=indi, cita=cita, asso=asso, chan=chan, famc=famc, obje=obje, repo=repo, sour=sour, srci=srci, subm=subm, even=even, pnpi=pnpi, plac=plac, _sort=sort)
        return note_stru

    # ------------- Repo ---------------
    def repo_record(self, item):
        xref = self.extract_xref(item.tag, item.xref_id)
        if RepositoryRecord.objects.filter(tree=self.tree, xref=xref).exists():
            repo = RepositoryRecord.objects.filter(tree=self.tree, xref=xref).get()
        else:
            sort = len(RepositoryRecord.objects.filter(tree=self.tree)) + 1
            repo = RepositoryRecord.objects.create(tree=self.tree, xref=xref, _sort=sort)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'NAME': repo.name = self.get_name(x.value)
                case 'ADDR'|'PHON'|'EMAIL'|'FAX'|'WWW': repo.addr = self.address_struct(x, repo.addr, 'RepositoryRecord_' + str(repo.id))
                case 'NOTE': self.note_struct(x, repo=repo)
                case 'REFN': self.user_ref_num(x, repo=repo)
                case 'RIN':  repo.rin  = x.value
                case 'CHAN': repo.chan = x.value
                case _: self.unexpected_tag(x)
        repo.save()

    # ------------- Source ---------------
    def source_record(self, item):
        xref = self.extract_xref(item.tag, item.xref_id)
        if SourceRecord.objects.filter(tree=self.tree, xref=xref).exists():
            sour = SourceRecord.objects.filter(tree=self.tree, xref=xref).get()
        else:
            sort = len(SourceRecord.objects.filter(tree=self.tree)) + 1
            sour = SourceRecord.objects.create(tree=self.tree, xref=xref, _sort=sort)
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
                case 'OBJE': self.media_link(x, sour=sour)
                case '_UPD': sour._upd = x.value
                case '_TYPE': sour._type = x.value
                case '_MEDI': sour._medi = x.value
                case '_UID': sour._uid = x.value
                case _: self.unexpected_tag(x)
        sour.save()

    def source_data(self, item, sour):
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'EVEN': 
                    sour.data_even = x.value
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'DATE': sour.data_date = y.value
                            case 'PLAC': sour.data_plac = y.value
                            case _: self.unexpected_tag(y)
                case 'AGNC': sour.data_agnc = x.value
                case _: self.unexpected_tag(x)

    def source_repo_link(self, item, sour):
        xref = self.extract_xref('REPO', item.value)
        if RepositoryRecord.objects.filter(tree=self.tree, xref=xref).exists():
            repo = RepositoryRecord.objects.filter(tree=self.tree, xref=xref).get()
        else:
            sort = len(RepositoryRecord.objects.filter(tree=self.tree)) + 1
            repo = RepositoryRecord.objects.create(tree=self.tree, xref=xref, _sort=sort)
        sort = len(SourceRepositoryCitation.objects.filter(repo=repo, sour=sour)) + 1
        srci = SourceRepositoryCitation.objects.create(repo=repo, sour=sour, _sort=sort)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'CALN': 
                    srci.caln = x.value
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'MEDI': srci.caln_medi = y.value
                            case _: self.unexpected_tag(y)
                case 'NOTE': self.note_struct(x, srci=srci)
                case _: self.unexpected_tag(x)
        srci.save()

    def source_citat(self, item, fam=None, indi=None, asso=None, obje=None, even=None, pnpi=None, note=None, ):
        xref = self.extract_xref('SOUR', item.value)
        if SourceRecord.objects.filter(tree=self.tree, xref=xref).exists():
            sour = SourceRecord.objects.filter(tree=self.tree, xref=xref).get()
        else:
            sort = len(SourceRecord.objects.filter(tree=self.tree)) + 1
            sour = SourceRecord.objects.create(tree=self.tree, xref=xref, _sort=sort)
        sort = len(SourceCitation.objects.filter(fam=fam, indi=indi, asso=asso, obje=obje, even=even, pnpi=pnpi, note=note)) + 1
        cita = SourceCitation.objects.create(sour=sour, fam=fam, indi=indi, asso=asso, obje=obje, even=even, pnpi=pnpi, note=note, _sort=sort)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'PAGE': cita.page = x.value
                case 'EVEN': 
                    cita.even_even = x.value
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'ROLE': cita.even_role = y.value
                            case _: self.unexpected_tag(y)
                case 'DATA':
                    for y in x.sub_tags(follow=False):
                        match y.tag:
                            case 'DATE': cita.data_date = y.value
                            case 'TEXT': cita.data_text = y.value
                            case _: self.unexpected_tag(y)
                case 'OBJE': self.media_link(x, cita=cita)
                case 'NOTE': self.note_struct(x, cita=cita)
                case 'QUAY': cita.quay = x.value
                case 'AUTH': cita.auth = x.value # ?
                case 'TITL': cita.titl = x.value # ?
                case '_UPD': cita._upd = x.value
                case '_TYPE': cita._type = x.value
                case '_MEDI': cita._medi = x.value
                case _: self.unexpected_tag(x)
        cita.save()

    # ------------- Submitter ---------------
    def submit_record(self, item):
        xref = self.extract_xref(item.tag, item.xref_id)
        sort = len(SubmitterRecord.objects.filter(tree=self.tree)) + 1
        subm = SubmitterRecord.objects.create(tree=self.tree, xref=xref, _sort=sort)
        if (self.head_subm == xref):
            self.tree.subm_id = subm.id
            self.tree.save()
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'NAME': subm.name = self.get_name(x.value)
                case 'ADDR'|'PHON'|'EMAIL'|'FAX'|'WWW': subm.addr = self.address_struct(x, subm.addr, 'SubmitterRecord_' + str(subm.id))
                case 'OBJE': self.media_link(x, subm=subm)
                case 'RIN':  subm.rin  = x.value
                case 'NOTE': self.note_struct(x, subm=subm)
                case 'CHAN': subm.chan = self.change_date(x, 'SubmitterRecord_' + str(subm.id))
                case '_UID': subm._uid = x.value
                case _: self.unexpected_tag(x)
        subm.save()

    # ------------- Album ---------------
    def album_record(self, item, xref=None):
        if not xref:
            xref = self.extract_xref('_ALBUM', item.xref_id)
        if AlbumRecord.objects.filter(tree=self.tree.id, xref=xref).exists():
            album = AlbumRecord.objects.filter(tree=self.tree.id, xref=xref).get()
        else:
            sort = len(AlbumRecord.objects.filter(tree=self.tree)) + 1
            album = AlbumRecord.objects.create(tree=self.tree, xref=xref, _sort=sort)
        for x in item.sub_tags(follow=False):
            match x.tag:
                case 'TITL': album.titl = x.value
                case 'DESCRIPTION': album.desc = x.value
                case '_UPD': album._upd = x.value
                case 'RIN':  album.rin  = x.value
                case _: self.unexpected_tag(x)
        album.save()
        return album

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
                case 'NOTE': self.note_struct(x, plac=plac)
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

    def event_detail(self, x, deta):
        if not deta:
            deta = EventDetail.objects.create()
        age = None
        match x.tag:
            case 'TYPE': deta.type = x.value
            case 'AGE':  age  = x.value
            case 'DATE': 
                if (str(x.value) not in (',,', '..', '.')) and ('неизв' not in str(x.value).replace(' ', '').lower()):
                    deta.date = x.value
            case 'PLAC': deta.plac = self.place_struct(x)
            case 'ADDR'|'PHON'|'EMAIL'|'FAX'|'WWW': deta.addr = self.address_struct(x, deta.addr, 'EventDetail_' + str(deta.id))
            case 'AGNC': deta.agnc = x.value
            case 'RELI': deta.reli = x.value
            case 'CAUS': deta.caus = x.value
            case 'SOUR': self.source_citat(x, even=deta)
            case 'NOTE': self.note_struct(x, even=deta)
            case 'OBJE': self.media_link(x, even=deta)
            case _: self.unexpected_tag(x)
        deta.save()
        return deta, age

    def find_person(self, xref):
        if IndividualRecord.objects.filter(tree=self.tree, xref=xref).exists():
            return IndividualRecord.objects.filter(tree=self.tree, xref=xref)[0]
        return None

    def find_pers_by_id(self, person_id):
        if IndividualRecord.objects.filter(tree=self.tree, id=person_id).exists():
            return IndividualRecord.objects.filter(tree=self.tree, id=person_id).get()
        return None

    def find_family(self, xref):
        xref = self.extract_xref('FAM', xref)
        if FamRecord.objects.filter(tree=self.tree, xref=xref).exists():
            return FamRecord.objects.filter(tree=self.tree, xref=xref)[0]
        return None

    def extract_xref(self, tag, value):
        liter = LITERS[tag]
        if value and ('@' + liter) in value:
            return int(value.split('@' + liter)[1].split('@')[0])

    def user_ref_num(self, item, indi=None, obje=None, note=None, repo=None, sour=None):
        sort = len(UserReferenceNumber.objects.filter(indi=indi, obje=obje, note=note, repo=repo, sour=sour)) + 1
        refn = UserReferenceNumber.objects.create(refn=item.value, indi=indi, obje=obje, note=note, repo=repo, sour=sour, _sort=sort)
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
        ret = str(item.offset) + ', tag: ' + item.tag
        if item.xref_id:
            ret += ', xref_id: ' + item.xref_id
        if item.value:
            ret += ', value: ' + item.value
        if item.tag.startswith('_'):
            print('Unexpected tag. Offset: ' + ret)
        else:
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

