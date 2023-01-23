import os, io
from datetime import datetime
from django.urls import reverse
from django.shortcuts import get_object_or_404
from family.models import (FamTreeUser, AssociationStructure, FamTree, IndividualRecord, FamRecord, MultimediaLink, MultimediaRecord, #PersonalNamePieces, 
    PersonalNameStructure, SourceRecord, AlbumRecord, ChangeDate, SubmitterRecord, NoteStructure, NamePhoneticVariation, 
    NameRomanizedVariation, SourceCitation, IndividualEventStructure, IndividualAttributeStructure, ChildToFamilyLink, 
    UserReferenceNumber, FamilyEventStructure, NoteRecord, RepositoryRecord, SourceRepositoryCitation,
    MultimediaFile)
from family.const import *
from logs.models import ServiceTask, ServiceTaskStatus

class ExpGedcom551:
    task: ServiceTask

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.custom_fields = True

    def export_gedcom_551(self, folder, pk=0, task_id=None):
        if (not os.path.isdir(folder)):
            return {
                'result': 'error', 
                'folder': folder,
                'description': 'Folder does not exist.',
                }
        self.use_xref = False
        if pk:
            tree = get_object_or_404(FamTree.objects.filter(id=pk))
            if self.can_export(tree):
                if task_id and ServiceTask.objects.filter(id=task_id).exists():
                    self.task = ServiceTask.objects.filter(id=task_id).get()
                self.exp_tree_to_file(folder, tree)
        else:
            for tree in FamTree.objects.all():
                if self.can_export(tree):
                    self.exp_tree_to_file(folder, tree)
        return {'result': 'ok'}

    def export_gedcom_551_str(self, tree: FamTree):
        self.use_xref = False
        self.f = io.StringIO()
        self.exp_tree(tree)
        return self.f.getvalue()

    def can_export(self, tree):
        q1 = (len(IndividualRecord.objects.filter(tree=tree)) > 0)
        q2 = (len(FamRecord.objects.filter(tree=tree)) > 0)
        return (q1 or q2)

    def exp_tree_to_file(self, folder, tree):
        fname = tree.get_file_name()
        self.f = open(folder + '\\' + fname, 'w', encoding='utf-8-sig')
        self.exp_tree(tree)
        self.f.close()

    def exp_tree(self, tree):
        self.write_header(tree)
        for x in SubmitterRecord.objects.filter(tree=tree).order_by('_sort'):
            self.submitter_record(x)
        for x in AlbumRecord.objects.filter(tree=tree).order_by('_sort'):
            self.album_record(x)
        for x in IndividualRecord.objects.filter(tree=tree).order_by('_sort'):
            self.indi_record(x)
        for x in FamRecord.objects.filter(tree=tree).order_by('_sort'):
            self.fam_record(x)
        for x in MultimediaRecord.objects.filter(tree=tree).order_by('_sort'):
            self.media_record(x)
        for x in SourceRecord.objects.filter(tree=tree).order_by('_sort'):
            self.source_record(x)
        for x in RepositoryRecord.objects.filter(tree=tree).order_by('_sort'):
            self.repo_record(x)
        for x in NoteRecord.objects.filter(tree=tree).order_by('_sort'):
            self.note_record(x)
        self.write_required(0, 'TRLR')

    # TODO: print self values
    def write_header(self, tree):
        site = os.environ.get('DJANGO_HOST_MAIL', '')
        addr = os.environ.get('DJANGO_HOST_ADDR', '')
        name = tree.name
        if not name:
            name = tree.file
        self.write_required(0, 'HEAD')
        self.write_required(1, 'SOUR', site.upper())
        self.write_optional(2, 'VERS', '5.5.1')
        self.write_optional(2, 'NAME', f'Family Tree "{name}" from {site}')
        self.write_required(2, 'CORP', site)
        self.write_required(3, 'ADDR')
        self.write_optional(4, 'CITY', addr.split(',')[0].strip())
        self.write_optional(4, 'STAE', addr.split(',')[1].strip())
        self.write_optional(4, 'CTRY', addr.split(',')[2].strip())
        self.write_optional(1, 'DEST', site.upper())
        self.write_optional(1, 'DATE', datetime.now().strftime('%d %b %Y').upper())
        self.write_optional(2, 'TIME', datetime.now().strftime('%H:%M:%S'))
        if tree.subm_id:
            subm = SubmitterRecord.objects.filter(id=tree.subm_id).get()
            self.write_link(1, 'SUBM', subm._sort, subm.id)
        self.write_optional(1, 'FILE', tree.file)
        self.write_optional(1, 'COPR', tree.copr)
        self.write_required(1, 'GEDC')
        self.write_optional(2, 'VERS', tree.gedc_vers)
        self.write_optional(2, 'FORM', tree.gedc_form)
        self.write_optional(1, 'CHAR', tree.char)
        self.write_optional(2, 'VERS', tree.char_vers)
        self.write_optional(1, 'LANG', tree.lang)
        self.write_text(1, 'NOTE', tree.note)

    def submitter_record(self, subm):
        self.write_id('SUBM', subm._sort, subm.id)
        self.write_optional(1, 'NAME', subm.name)
        self.write_address(1, subm.addr)
        for x in MultimediaLink.objects.filter(subm=subm.id).order_by('_sort'):
            self.write_media_link(1, x)
        self.write_optional(1, 'RIN', subm.rin)
        for x in NoteStructure.objects.filter(subm=subm.id).order_by('_sort'):
            self.write_note_link(1, x)
        self.write_chan(1, subm.chan)
        self.write_custom(1, '_UID', subm._uid)
        self.inc_task_value()

    def indi_record(self, indi):
        self.write_id('INDI', indi._sort, indi.id)
        for x in PersonalNameStructure.objects.filter(indi=indi.id).order_by('_sort'):
            self.write_name(1, x)
        self.write_optional(1, 'SEX', indi.sex)
        for x in IndividualEventStructure.objects.filter(indi=indi.id).order_by('_sort'):
            self.write_indi_event(1, x)
        for x in IndividualAttributeStructure.objects.filter(indi=indi.id).order_by('_sort'):
            self.write_indi_attr(1, x)
        for x in ChildToFamilyLink.objects.filter(chil=indi.id).order_by('_sort'):
            self.write_child_family(1, x)
        for x in FamRecord.objects.filter(husb=indi.id).order_by('_sort'):
            self.write_spouse(1, x)
        for x in FamRecord.objects.filter(wife=indi.id).order_by('_sort'):
            self.write_spouse(1, x)
        for x in AssociationStructure.objects.filter(indi=indi.id).order_by('_sort'):
            self.write_asso_link(1, x)
        for x in UserReferenceNumber.objects.filter(indi=indi.id).order_by('_sort'):
            self.write_refn(1, x)
        self.write_optional(1, 'RIN', indi.rin)
        self.write_chan(1, indi.chan)
        for x in NoteStructure.objects.filter(indi=indi.id).order_by('_sort'):
            self.write_note_link(1, x)
        for x in SourceCitation.objects.filter(indi=indi.id).order_by('_sort'):
            self.write_citate(1, x)
        for x in MultimediaLink.objects.filter(indi=indi.id).order_by('_sort'):
            self.write_media_link(1, x)
        self.write_custom(1, '_UPD', indi._upd)
        self.write_custom(1, '_UID', indi._uid)
        self.inc_task_value()
            
    def inc_task_value(self):
        if hasattr(self, 'task') and self.task and self.task.done != None:
            self.task.done += 1
            self.task.save()

    def make_xref(self, tag, xref, id=None):
        liter = LITERS[tag]
        if self.use_xref or not id:
            return '@' + liter + str(xref) + '@'
        return '@' + liter + str(id) + '@'

    def fam_record(self, fam):
        self.write_id('FAM', fam._sort, fam.id)
        for x in FamilyEventStructure.objects.filter(fam=fam.id).order_by('_sort'):
            self.write_fam_event(1, x)
        if fam.husb:
            self.write_optional(1, 'HUSB', self.make_xref('INDI', fam.husb._sort, fam.husb.id))
        if fam.wife:
            self.write_optional(1, 'WIFE', self.make_xref('INDI', fam.wife._sort, fam.wife.id))
        for x in ChildToFamilyLink.objects.filter(fami=fam.id).order_by('_sort'):
            self.write_family_child(1, x)
        self.write_optional(1, 'NCHI', fam.nchi)
        for x in UserReferenceNumber.objects.filter(fam=fam.id).order_by('_sort'):
            self.write_refn(1, x)
        self.write_optional(1, 'RIN', fam.rin)
        self.write_chan(1, fam.chan)
        for x in NoteStructure.objects.filter(fam=fam.id).order_by('_sort'):
            self.write_note_link(1, x)
        for x in SourceCitation.objects.filter(fam=fam.id).order_by('_sort'):
            self.write_citate(1, x)
        for x in MultimediaLink.objects.filter(fam=fam.id).order_by('_sort'):
            self.write_media_link(1, x)
        self.write_custom(1, '_UID', fam._uid)
        self.write_custom(1, '_UPD', fam._upd)
        self.write_custom(1, '_MSTAT', fam._mstat)
        self.inc_task_value()

    def media_record(self, obje):
        self.write_id('OBJE', obje._sort, obje.id)
        for x in MultimediaFile.objects.filter(obje=obje.id).order_by('_sort'):
            if x.file:
                fname = x.file.split('/')[-1]
                host = os.environ.get('DJANGO_HOST_API', '')
                url = host + reverse('family:doc', args=('pedigree', obje.tree.id, fname))
                self.write_optional(1, 'FILE', url)
            self.write_optional(2, 'FORM', x.form)
            self.write_optional(3, 'TYPE', x.type)
            self.write_optional(2, 'TITL', x.titl)
        for x in UserReferenceNumber.objects.filter(obje=obje.id).order_by('_sort'):
            self.write_refn(1, x)
        self.write_optional(1, 'RIN', obje.rin)
        for x in NoteStructure.objects.filter(obje=obje.id).order_by('_sort'):
            self.write_note_link(1, x)
        for x in SourceCitation.objects.filter(obje=obje.id).order_by('_sort'):
            self.write_citate(1, x)
        self.write_chan(1, obje.chan)
        self.write_custom(1, '_FILESIZE', obje._size)
        self.write_custom(1, '_DATE', obje._date)
        self.write_custom(1, '_PLACE', obje._plac)
        self.write_custom(1, '_PRIM', obje._prim)
        self.write_custom(1, '_CUTOUT', obje._cuto)
        self.write_custom(1, '_PARENTRIN', obje._pari)
        self.write_custom(1, '_PERSONALPHOTO', obje._pers)
        self.write_custom(1, '_PRIM_CUTOUT', obje._prcu)
        self.write_custom(1, '_PARENTPHOTO', obje._pare)
        self.write_custom(1, '_PHOTO_RIN', obje._prin)
        self.write_custom(1, '_POSITION', obje._posi)
        if obje._albu:
            self.write_custom(1, '_ALBUM', self.make_xref('_ALBUM', obje._albu._sort, obje._albu.id))
        self.write_custom(1, '_UID', obje._uid )
        self.inc_task_value()

    def source_record(self, sour):
        self.write_id('SOUR', sour._sort, sour.id)
        if (sour.data_even or sour.data_date or sour.data_plac or sour.data_agnc):
            self.write_required(1, 'DATA')
            self.write_optional(2, 'EVEN', sour.data_even)
            self.write_optional(3, 'DATE', sour.data_date)
            self.write_optional(3, 'PLAC', sour.data_plac)
            self.write_optional(2, 'AGNC', sour.data_agnc)
        self.write_text(1, 'AUTH', sour.auth)
        self.write_text(1, 'TITL', sour.titl)
        self.write_optional(1, 'ABBR', sour.abbr)
        self.write_text(1, 'PUBL', sour.publ)
        self.write_text(1, 'TEXT', sour.text)
        for x in SourceRepositoryCitation.objects.filter(sour=sour.id).order_by('_sort'):
            self.write_repo_citate(1, x)
        for x in UserReferenceNumber.objects.filter(sour=sour.id).order_by('_sort'):
            self.write_refn(1, x)
        self.write_optional(1, 'RIN', sour.rin)
        self.write_chan(1, sour.chan)
        for x in NoteStructure.objects.filter(sour=sour.id).order_by('_sort'):
            self.write_note_link(1, x)
        for x in MultimediaLink.objects.filter(sour=sour.id).order_by('_sort'):
            self.write_media_link(1, x)
        self.write_custom(1, '_UPD', sour._upd)
        self.write_custom(1, '_TYPE', sour._type)
        self.write_custom(1, '_MEDI', sour._medi)
        self.write_custom(1, '_UID', sour._uid)
        self.inc_task_value()

    def repo_record(self, repo):
        self.write_id('REPO', repo._sort, repo.id)
        self.write_required(1, 'NAME', repo.name)
        self.write_address(1, repo.addr)
        for x in NoteStructure.objects.filter(repo=repo.id).order_by('_sort'):
            self.write_note_link(1, x)
        for x in UserReferenceNumber.objects.filter(repo=repo.id).order_by('_sort'):
            self.write_refn(1, x)
        self.write_optional(1, 'RIN', repo.rin)
        self.write_chan(1, repo.chan)
        self.inc_task_value()

    def note_record(self, note):
        self.write_text(0, self.make_xref('NOTE', note._sort, note.id) + ' NOTE', note.note)
        self.inc_task_value()


    def album_record(self, albu):
        self.write_id('_ALBUM', albu._sort, albu.id)
        self.write_optional(1, 'TITL', albu.titl)
        self.write_custom(1, '_UPD', albu._upd)
        self.inc_task_value()

    # ------ Tools --------

    def write_id(self, tag, xref, id=None):
        self.f.write('0 ' + self.make_xref(tag, xref, id) + ' ' + tag + '\n')

    def write_link(self, level, tag, xref, id=None):
        if self.use_xref or (id != None):
            self.write_optional(level, tag, self.make_xref(tag, xref, id))

    def write_required(self, level, tag, value=''):
        s_value = ''
        if value:
            s_value = ' ' + value
        self.f.write(str(level) + ' ' + tag + s_value + '\n')

    def write_optional(self, level, tag, value):
        if value:
            if (type(value) != ChangeDate):
                self.f.write(str(level) + ' ' + tag + ' ' + value + '\n')
            else:
                date = value.get_date()
                time = value.get_time()
                if date:
                    self.f.write(str(level) + ' DATE ' + date + '\n')
                    if time:
                        self.f.write(str(level+1) + ' TIME ' + time + '\n')

    def write_custom(self, level, tag, value):
        if self.custom_fields:
            self.write_optional(level, tag, value)

    def write_text(self, level, tag, text):
        if not text:
            return
        first_note = True
        lines = text.split('\n')
        for line in lines:
            first_line = True
            rest = line.strip()
            while rest:
                part = rest
                if (len(rest) > 120):
                    pos1 = rest[:120].rfind(' ')
                    while (pos1 > 1 and rest[pos1-1] == ' '):
                        pos1 -= 1
                    pos2 = pos1
                    while (pos1 > 1 and (pos1-pos2 < 4)):
                        pos2 = pos1
                        while (pos2 > 1 and rest[pos2-1] != ' '):
                            pos2 -= 1
                        if (pos1-pos2 < 4):
                            pos1 = pos2
                        while (pos1 > 1 and rest[pos1-1] == ' '):
                            pos1 -= 1
                    if (pos1 > 1):
                        pos1 = pos2 + int((pos1-pos2)/2)
                        part = rest[:pos1]
                rest = rest[len(part):]
                if first_note:
                    self.write_required(level, tag, part)
                    first_note = False
                else:
                    if first_line:
                        self.write_required(level+1, 'CONT', part)
                    else:
                        self.write_required(level+1, 'CONC', part)
                first_line = False

    def write_address(self, level, addr):
        if addr:
            self.write_required(level, 'ADDR')
            self.write_optional(level+1, 'ADR1', addr.addr_adr1)
            self.write_optional(level+1, 'ADR2', addr.addr_adr2)
            self.write_optional(level+1, 'ADR3', addr.addr_adr3)
            self.write_optional(level+1, 'CITY', addr.addr_city)
            self.write_optional(level+1, 'STAE', addr.addr_stae)
            self.write_optional(level+1, 'POST', addr.addr_post)
            self.write_optional(level+1, 'CTRY', addr.addr_ctry)
            self.write_optional(level, 'PHON', addr.phon)
            self.write_optional(level, 'PHON', addr.phon2)
            self.write_optional(level, 'PHON', addr.phon3)
            self.write_optional(level, 'EMAIL', self.safe(addr.email))
            self.write_optional(level, 'EMAIL', self.safe(addr.email2))
            self.write_optional(level, 'EMAIL', self.safe(addr.email3))
            self.write_optional(level, 'FAX', addr.fax)
            self.write_optional(level, 'FAX', addr.fax2)
            self.write_optional(level, 'FAX', addr.fax3)
            self.write_optional(level, 'WWW', addr.www)
            self.write_optional(level, 'WWW', addr.www2)
            self.write_optional(level, 'WWW', addr.www3)

    def safe(self, value):
        if value:
            return value.replace('@', '@@')

    def write_place(self, level, plac):
        if plac:
            self.write_required(level, 'PLAC', plac.name)
            for x in NamePhoneticVariation.objects.filter(plac=plac.id):
                self.write_phonetic(level+1, x)
            for x in NameRomanizedVariation.objects.filter(plac=plac.id):
                self.write_romanized(level+1, x)
            if (plac.map_lati or plac.map_long):
                self.write_required(level+1, 'MAP')
                self.write_optional(level+2, 'LATI', plac.map_lati)
                self.write_optional(level+2, 'LONG', plac.map_long)
                for x in NoteStructure.objects.filter(plac=plac.id).order_by('_sort'):
                    self.write_note_link(level, x)

    def write_note_link(self, level, note_struct):
        if note_struct and note_struct.note:
            if self.use_xref:
                self.write_text(level, 'NOTE', '@N' + str(note_struct.note._sort) + '@')
            else:
                self.write_text(level, 'NOTE', '@N' + str(note_struct.note.id) + '@')

    def write_chan(self, level, chan):
        if chan:
            self.write_required(level, 'CHAN')
            self.write_optional(level+1, 'DATE', chan.date)
            self.write_optional(level+2, 'TIME', chan.time)

    def write_name(self, level, name):
        value = ''
        if name.piec and name.piec.givn:
            value = name.piec.givn
        if name.piec and name.piec.surn:
            if value:
                value += ' '
            value += '/' + name.piec.surn + '/'
        self.write_required(level, 'NAME', value)
        self.write_optional(level+1, 'TYPE', name.type)
        self.write_name_pieces(level+1, name.piec)
        for x in NamePhoneticVariation.objects.filter(name=name.id):
            self.write_phonetic(level+1, x)
        for x in NameRomanizedVariation.objects.filter(name=name.id):
            self.write_romanized(level+1, x)

    def write_name_pieces(self, level, piec):
        if piec:
            self.write_optional(level, 'NPFX', piec.npfx)
            self.write_optional(level, 'GIVN', piec.givn)
            self.write_optional(level, 'NICK', piec.nick)
            self.write_optional(level, 'SPFX', piec.spfx)
            self.write_optional(level, 'SURN', piec.surn)
            self.write_optional(level, 'NSFX', piec.nsfx)
            self.write_optional(level, 'NPFX', piec.npfx)
            self.write_custom(level, '_MARNM', piec._marnm)
            for x in NoteStructure.objects.filter(pnpi=piec.id).order_by('_sort'):
                self.write_note_link(level, x)
            for x in SourceCitation.objects.filter(pnpi=piec.id).order_by('_sort'):
                self.write_citate(level, x)

    def write_phonetic(self, level, phon):
        self.write_required(level, 'FONE', phon.value)
        self.write_optional(level+1, 'TYPE', phon.type)
        self.write_name_pieces(level+1, phon.piec)

    def write_romanized(self, level, roma):
        self.write_required(level, 'ROMN', roma.value)
        self.write_optional(level+1, 'TYPE', roma.type)
        self.write_name_pieces(level+1, roma.piec)

    def write_citate(self, level, cita):
        self.write_link(level, 'SOUR', cita.sour._sort, cita.sour.id)
        self.write_optional(level+1, 'PAGE', cita.page)
        self.write_optional(level+1, 'EVEN', cita.even_even)
        self.write_optional(level+2, 'ROLE', cita.even_role)
        if (cita.data_date or cita.data_text):
            self.write_required(level+1, 'DATA')
        self.write_optional(level+2, 'DATE', cita.data_date)
        self.write_text(level+2, 'TEXT', cita.data_text) # TODO: many_to_one
        for x in MultimediaLink.objects.filter(cita=cita.id).order_by('_sort'):
            self.write_media_link(1, x)
        for x in NoteStructure.objects.filter(cita=cita.id).order_by('_sort'):
            self.write_note_link(1, x)
        self.write_optional(level+1, 'QUAY', cita.quay)

    def write_repo_citate(self, level, srci):
        self.write_link(level, 'REPO', srci.repo._sort, srci.repo.id)
        self.write_optional(level+1, 'CALN', srci.caln)
        self.write_optional(level+2, 'MEDI', srci.caln_medi)

    def write_indi_event(self, level, even):
        self.write_required(level, even.tag, even.value)
        self.write_event_detail(level+1, even.deta)
        self.write_optional(level+1, 'AGE',  even.age)
        #self.write_child(level, even.famc) # ???
        if even.famc:
            self.write_optional(level+1, 'ADOP', even.adop)

    def write_indi_attr(self, level, attr):
        if attr.value and (len(attr.value) > 120):
            self.write_text(level, attr.tag, attr.value)
        else:
            self.write_required(level, attr.tag, attr.value)
        self.write_event_detail(level+1, attr.deta)
        self.write_optional(level+1, 'TYPE', attr.type)

    def write_fam_event(self, level, even):
        self.write_required(level, even.tag, even.value)
        if even.husb_age:
            self.write_required(level+1, 'HUSB')
            self.write_required(level+2, 'AGE', even.husb_age)
        if even.wife_age:
            self.write_required(level+1, 'WIFE')
            self.write_required(level+2, 'AGE', even.husb_age)
        self.write_event_detail(level+1, even.deta)

    def write_event_detail(self, level, deta):
        if deta:
            self.write_optional(level, 'TYPE', deta.type)
            self.write_optional(level, 'DATE', deta.date)
            self.write_place(level, deta.plac)
            self.write_address(level, deta.addr)
            self.write_optional(level, 'AGNC', deta.agnc)
            self.write_optional(level, 'RELI', deta.reli)
            self.write_optional(level, 'CAUS', deta.caus)
            for x in NoteStructure.objects.filter(even=deta.id).order_by('_sort'):
                self.write_note_link(level, x)
            for x in SourceCitation.objects.filter(even=deta.id).order_by('_sort'):
                self.write_citate(level, x)
            for x in MultimediaLink.objects.filter(even=deta.id).order_by('_sort'):
                self.write_media_link(level, x)

    def write_child_family(self, level, ctfl):
        if ctfl and ctfl.fami:
            if self.use_xref:
                self.write_required(level, 'FAMC', '@F' + str(ctfl.fami._sort) + '@')
            else:
                self.write_required(level, 'FAMC', '@F' + str(ctfl.fami.id) + '@')
            self.write_optional(level+1, 'PEDI', ctfl.pedi)

    def write_family_child(self, level, ctfl):
        if ctfl and ctfl.chil:
            if self.use_xref:
                self.write_required(level, 'CHIL', '@I' + str(ctfl.chil._sort) + '@')
            else:
                self.write_required(level, 'CHIL', '@I' + str(ctfl.chil.id) + '@')

    def write_spouse(self, level, fam):
        if fam:
            if self.use_xref:
                self.write_required(level, 'FAMS', '@F' + str(fam._sort) + '@')
            else:
                self.write_required(level, 'FAMS', '@F' + str(fam.id) + '@')

    def write_asso_link(self, level, asso):
        self.write_required(level, 'ASSO', '@I' + str(asso.id) + '@')
        self.write_optional(level+1, 'RELA', asso.asso_rela)
        for x in SourceCitation.objects.filter(asso=asso.id).order_by('_sort'):
            self.write_citate(level+1, x)
        for x in NoteStructure.objects.filter(asso=asso.id).order_by('_sort'):
            self.write_note_link(level+1, x)

    def write_refn(self, level, refn):
        self.write_optional(level, 'REFN', refn.refn)
        self.write_optional(level+1, 'TYPE', refn.type)

    def write_media_link(self, level, media):
        if media.obje:
            if self.use_xref:
                self.write_required(level, 'OBJE', '@M' + str(media.obje._sort) + '@')
            else:
                self.write_required(level, 'OBJE', '@M' + str(media.obje.id) + '@')

def export_params(user, item_id) -> tuple[int, str]:
    total = 0
    if FamTreeUser.objects.filter(user_id=user.id, tree_id=item_id, can_view=True).exists():
        if FamTree.objects.filter(id=item_id).exists():
            tree = FamTree.objects.filter(id=item_id).get()
            total += len(IndividualRecord.objects.filter(tree=tree.id))
            total += len(FamRecord.objects.filter(tree=tree.id))
            total += len(NoteRecord.objects.filter(tree=tree.id))
            total += len(RepositoryRecord.objects.filter(tree=tree.id))
            total += len(SourceRecord.objects.filter(tree=tree.id))
            total += len(SubmitterRecord.objects.filter(tree=tree.id))
            total += len(AlbumRecord.objects.filter(tree=tree.id))
            total += len(MultimediaRecord.objects.filter(tree=tree.id))
            total += len(NoteStructure.objects.filter(tree=tree.id))
            if total == 0:
                return 0, f'Empty family tree with ID {item_id}'
            return total, ''
    return 0, f'Family tree with ID {item_id} not found'

def export_start(user, item_id, task_id) -> dict:
    if FamTreeUser.objects.filter(user_id=user.id, tree_id=item_id, can_view=True).exists():
        tree = FamTree.objects.filter(id=item_id).get()
        store_dir = tree.get_export_path(user)
        mgr = ExpGedcom551(user)
        mgr.export_gedcom_551(store_dir, pk=tree.id, task_id=task_id)
        return {'status':'completed', 'info': ''}
    return {'status':'warning', 'info': f'Family tree with id {task_id} not found'}
