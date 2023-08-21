import os, io
from datetime import datetime
from django.contrib.auth.models import User
from django.urls import reverse
from django.shortcuts import get_object_or_404
from family.models import (FamTreeUser, AssociationStructure, FamTree, IndividualRecord, FamRecord, MultimediaLink, MultimediaRecord, #PersonalNamePieces, 
    PersonalNameStructure, SourceRecord, AlbumRecord, ChangeDate, SubmitterRecord, NoteStructure, NamePhoneticVariation, 
    NameRomanizedVariation, SourceCitation, IndividualEventStructure, IndividualAttributeStructure, ChildToFamilyLink, 
    UserReferenceNumber, FamilyEventStructure, NoteRecord, RepositoryRecord, SourceRepositoryCitation,
    MultimediaFile, Gedcom)
from family.const import *
from logs.models import ServiceTask

class ExpGedcom551:
    user: User
    tree: FamTree
    task: ServiceTask
    custom_fields: bool
    light_version: bool
    save_to_model: bool
    row_num: int
    use_xref: bool

    def __init__(self, user: User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.custom_fields = True
        self.light_version = False
        self.save_to_model = False
        self.use_xref = False

    def export_gedcom_551(self, folder, pk=0, task_id=None):
        self.light_version = False
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
        self.light_version = False
        self.f = io.StringIO()
        self.exp_tree(tree)
        return self.f.getvalue()

    def export_gedcom_551_light(self, tree: FamTree):
        self.use_xref = False
        self.light_version = True
        self.f = io.StringIO()
        self.exp_tree(tree)
        return self.f.getvalue()

    def make_gedcom(self, tree_id, task_id=None):
        if not FamTreeUser.objects.filter(user_id=self.user.id, tree_id=tree_id).exists():
            return {'result': 'error', 'info': 'The specified tree does not exist or the user does not have permission to view it.'}
        if not FamTree.objects.filter(id=tree_id).exists():
            return {'result': 'error', 'info': 'The specified tree does not exist.'}
        if task_id and ServiceTask.objects.filter(id=task_id).exists():
            self.task = ServiceTask.objects.filter(id=task_id).get()
        self.tree = FamTree.objects.filter(id=tree_id).get()
        Gedcom.objects.filter(tree=tree_id).delete()
        self.light_version = False
        self.save_to_model = True
        self.exp_tree(self.tree)
        return {'result': 'ok'}

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
        self.row_num = 1
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

    def write_header(self, tree):
        if self.light_version:
            return
        site = os.environ.get('DJANGO_HOST_MAIL', '')
        addr = os.environ.get('DJANGO_HOST_ADDR', '')
        name = tree.name
        if not name:
            name = tree.file
        self.write_required(0, 'HEAD', used_by_chart=False)
        self.write_required(1, 'SOUR', site.upper(), used_by_chart=False)
        self.write_optional(2, 'VERS', '5.5.1', used_by_chart=False)
        self.write_optional(2, 'NAME', f'Family Tree "{name}" from {site}', used_by_chart=False)
        self.write_required(2, 'CORP', site, used_by_chart=False)
        self.write_required(3, 'ADDR', used_by_chart=False)
        self.write_optional(4, 'CITY', addr.split(',')[0].strip(), used_by_chart=False)
        self.write_optional(4, 'STAE', addr.split(',')[1].strip(), used_by_chart=False)
        self.write_optional(4, 'CTRY', addr.split(',')[2].strip(), used_by_chart=False)
        self.write_optional(1, 'DEST', site.upper(), used_by_chart=False)
        self.write_optional(1, 'DATE', datetime.now().strftime('%d %b %Y').upper(), used_by_chart=False)
        self.write_optional(2, 'TIME', datetime.now().strftime('%H:%M:%S'), used_by_chart=False)
        if tree.subm_id:
            subm = SubmitterRecord.objects.filter(id=tree.subm_id).get()
            self.write_link(1, 'SUBM', subm._sort, subm.id, used_by_chart=False)
        self.write_optional(1, 'FILE', tree.file, used_by_chart=False)
        self.write_optional(1, 'COPR', tree.copr, used_by_chart=False)
        self.write_required(1, 'GEDC', used_by_chart=False)
        self.write_optional(2, 'VERS', tree.gedc_vers, used_by_chart=False)
        self.write_optional(2, 'FORM', tree.gedc_form, used_by_chart=False)
        self.write_optional(1, 'CHAR', tree.char, used_by_chart=False)
        self.write_optional(2, 'VERS', tree.char_vers, used_by_chart=False)
        self.write_optional(1, 'LANG', tree.lang, used_by_chart=False)
        self.write_text(1, 'NOTE', tree.note, used_by_chart=False)

    def submitter_record(self, subm):
        if self.light_version:
            return
        self.write_id('SUBM', subm._sort, subm.id, used_by_chart=False)
        self.write_optional(1, 'NAME', subm.name, used_by_chart=False)
        self.write_address(1, subm.addr, used_by_chart=False)
        for x in MultimediaLink.objects.filter(subm=subm.id).order_by('_sort'):
            self.write_media_link(1, x, used_by_chart=False)
        self.write_optional(1, 'RIN', subm.rin, used_by_chart=False)
        for x in NoteStructure.objects.filter(subm=subm.id).order_by('_sort'):
            self.write_note_link(1, x, used_by_chart=False)
        self.write_chan(1, subm.chan, used_by_chart=False)
        self.write_custom(1, '_UID', subm._uid, used_by_chart=False)
        self.inc_task_value()

    def indi_record(self, indi):
        self.write_id('INDI', indi._sort, indi.id)
        for x in PersonalNameStructure.objects.filter(indi=indi.id).order_by('_sort'):
            self.write_name(1, x)
        self.write_optional(1, 'SEX', indi.sex)
        for x in IndividualEventStructure.objects.filter(indi=indi.id).order_by('_sort'):
            self.write_indi_event(1, x)
        if not self.light_version:
            for x in IndividualAttributeStructure.objects.filter(indi=indi.id).order_by('_sort'):
                self.write_indi_attr(1, x, used_by_chart=False)
        for x in ChildToFamilyLink.objects.filter(chil=indi.id).order_by('_sort'):
            self.write_child_family(1, x)
        for x in FamRecord.objects.filter(husb=indi.id).order_by('_sort'):
            self.write_spouse(1, x)
        for x in FamRecord.objects.filter(wife=indi.id).order_by('_sort'):
            self.write_spouse(1, x)
        if not self.light_version:
            for x in AssociationStructure.objects.filter(indi=indi.id).order_by('_sort'):
                self.write_asso_link(1, x, used_by_chart=False)
            for x in UserReferenceNumber.objects.filter(indi=indi.id).order_by('_sort'):
                self.write_refn(1, x, used_by_chart=False)
            self.write_optional(1, 'RIN', indi.rin)
            self.write_chan(1, indi.chan, used_by_chart=False)
            for x in NoteStructure.objects.filter(indi=indi.id).order_by('_sort'):
                self.write_note_link(1, x, used_by_chart=False)
            for x in SourceCitation.objects.filter(indi=indi.id).order_by('_sort'):
                self.write_citate(1, x, used_by_chart=False)
        used_by_chart = True
        for x in MultimediaLink.objects.filter(indi=indi.id).order_by('_sort'):
            self.write_media_link(1, x, used_by_chart=used_by_chart)
            used_by_chart = False
            if self.light_version:
                break
        if not self.light_version:
            self.write_custom(1, '_UPD', indi._upd, used_by_chart=False)
            self.write_custom(1, '_UID', indi._uid, used_by_chart=False)
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
        if not self.light_version:
            for x in FamilyEventStructure.objects.filter(fam=fam.id).order_by('_sort'):
                self.write_fam_event(1, x, used_by_chart=False)
        if fam.husb:
            self.write_optional(1, 'HUSB', self.make_xref('INDI', fam.husb._sort, fam.husb.id))
        if fam.wife:
            self.write_optional(1, 'WIFE', self.make_xref('INDI', fam.wife._sort, fam.wife.id))
        for x in ChildToFamilyLink.objects.filter(fami=fam.id).order_by('_sort'):
            self.write_family_child(1, x)
        if not self.light_version:
            self.write_optional(1, 'NCHI', fam.nchi, used_by_chart=False)
            for x in UserReferenceNumber.objects.filter(fam=fam.id).order_by('_sort'):
                self.write_refn(1, x, used_by_chart=False)
            self.write_optional(1, 'RIN', fam.rin, used_by_chart=False)
            self.write_chan(1, fam.chan, used_by_chart=False)
            for x in NoteStructure.objects.filter(fam=fam.id).order_by('_sort'):
                self.write_note_link(1, x, used_by_chart=False)
            for x in SourceCitation.objects.filter(fam=fam.id).order_by('_sort'):
                self.write_citate(1, x, used_by_chart=False)
            for x in MultimediaLink.objects.filter(fam=fam.id).order_by('_sort'):
                self.write_media_link(1, x, used_by_chart=False)
            self.write_custom(1, '_UID', fam._uid, used_by_chart=False)
            self.write_custom(1, '_UPD', fam._upd, used_by_chart=False)
            self.write_custom(1, '_MSTAT', fam._mstat, used_by_chart=False)
        self.inc_task_value()

    def media_record(self, obje):
        self.write_id('OBJE', obje._sort, obje.id)
        used_by_chart = True
        for x in MultimediaFile.objects.filter(obje=obje.id).order_by('_sort'):
            if x.file:
                fname = x.file.split('/')[-1]
                host = ''
                if not self.light_version:
                    host = os.environ.get('DJANGO_HOST_API', '')
                url = host + reverse('family:doc', args=('pedigree', obje.tree.id, fname))
                self.write_optional(1, 'FILE', url, used_by_chart=used_by_chart)
            used_by_chart = False
            if self.light_version:
                break
            self.write_optional(2, 'FORM', x.form)
            self.write_optional(3, 'TYPE', x.type)
            self.write_optional(2, 'TITL', x.titl)
        if not self.light_version:
            for x in UserReferenceNumber.objects.filter(obje=obje.id).order_by('_sort'):
                self.write_refn(1, x, used_by_chart=False)
            self.write_optional(1, 'RIN', obje.rin)
            for x in NoteStructure.objects.filter(obje=obje.id).order_by('_sort'):
                self.write_note_link(1, x, used_by_chart=False)
            for x in SourceCitation.objects.filter(obje=obje.id).order_by('_sort'):
                self.write_citate(1, x, used_by_chart=False)
            self.write_chan(1, obje.chan, used_by_chart=False)
            self.write_custom(1, '_FILESIZE', obje._size, used_by_chart=False)
            self.write_custom(1, '_DATE', obje._date, used_by_chart=False)
            self.write_custom(1, '_PLACE', obje._plac, used_by_chart=False)
            self.write_custom(1, '_PRIM', obje._prim, used_by_chart=False)
            self.write_custom(1, '_CUTOUT', obje._cuto, used_by_chart=False)
            self.write_custom(1, '_PARENTRIN', obje._pari, used_by_chart=False)
            self.write_custom(1, '_PERSONALPHOTO', obje._pers, used_by_chart=False)
            self.write_custom(1, '_PRIM_CUTOUT', obje._prcu, used_by_chart=False)
            self.write_custom(1, '_PARENTPHOTO', obje._pare, used_by_chart=False)
            self.write_custom(1, '_PHOTO_RIN', obje._prin, used_by_chart=False)
            self.write_custom(1, '_POSITION', obje._posi, used_by_chart=False)
            if obje._albu:
                self.write_custom(1, '_ALBUM', self.make_xref('_ALBUM', obje._albu._sort, obje._albu.id), used_by_chart=False)
            self.write_custom(1, '_UID', obje._uid, used_by_chart=False)
        self.inc_task_value()

    def source_record(self, sour):
        if self.light_version:
            return
        self.write_id('SOUR', sour._sort, sour.id, used_by_chart=False)
        if (sour.data_even or sour.data_date or sour.data_plac or sour.data_agnc):
            self.write_required(1, 'DATA', used_by_chart=False)
            self.write_optional(2, 'EVEN', sour.data_even, used_by_chart=False)
            self.write_optional(3, 'DATE', sour.data_date, used_by_chart=False)
            self.write_optional(3, 'PLAC', sour.data_plac, used_by_chart=False)
            self.write_optional(2, 'AGNC', sour.data_agnc, used_by_chart=False)
        self.write_text(1, 'AUTH', sour.auth, used_by_chart=False)
        self.write_text(1, 'TITL', sour.titl, used_by_chart=False)
        self.write_optional(1, 'ABBR', sour.abbr, used_by_chart=False)
        self.write_text(1, 'PUBL', sour.publ, used_by_chart=False)
        self.write_text(1, 'TEXT', sour.text, used_by_chart=False)
        for x in SourceRepositoryCitation.objects.filter(sour=sour.id).order_by('_sort'):
            self.write_repo_citate(1, x, used_by_chart=False)
        for x in UserReferenceNumber.objects.filter(sour=sour.id).order_by('_sort'):
            self.write_refn(1, x, used_by_chart=False)
        self.write_optional(1, 'RIN', sour.rin, used_by_chart=False)
        self.write_chan(1, sour.chan, used_by_chart=False)
        for x in NoteStructure.objects.filter(sour=sour.id).order_by('_sort'):
            self.write_note_link(1, x, used_by_chart=False)
        for x in MultimediaLink.objects.filter(sour=sour.id).order_by('_sort'):
            self.write_media_link(1, x, used_by_chart=False)
        self.write_custom(1, '_UPD', sour._upd, used_by_chart=False)
        self.write_custom(1, '_TYPE', sour._type, used_by_chart=False)
        self.write_custom(1, '_MEDI', sour._medi, used_by_chart=False)
        self.write_custom(1, '_UID', sour._uid, used_by_chart=False)
        self.inc_task_value()

    def repo_record(self, repo):
        if self.light_version:
            return
        self.write_id('REPO', repo._sort, repo.id, used_by_chart=False)
        self.write_required(1, 'NAME', repo.name, used_by_chart=False)
        self.write_address(1, repo.addr, used_by_chart=False)
        for x in NoteStructure.objects.filter(repo=repo.id).order_by('_sort'):
            self.write_note_link(1, x, used_by_chart=False)
        for x in UserReferenceNumber.objects.filter(repo=repo.id).order_by('_sort'):
            self.write_refn(1, x, used_by_chart=False)
        self.write_optional(1, 'RIN', repo.rin, used_by_chart=False)
        self.write_chan(1, repo.chan, used_by_chart=False)
        self.inc_task_value()

    def note_record(self, note):
        if self.light_version:
            return
        self.write_text(0, self.make_xref('NOTE', note._sort, note.id) + ' NOTE', note.note, used_by_chart=False)
        self.inc_task_value()


    def album_record(self, albu):
        if self.light_version:
            return
        self.write_id('_ALBUM', albu._sort, albu.id, used_by_chart=False)
        self.write_optional(1, 'TITL', albu.titl, used_by_chart=False)
        self.write_custom(1, '_UPD', albu._upd, used_by_chart=False)
        self.inc_task_value()

    # ------ Tools --------

    def write_row(self, value, used_by_chart=True):
        if self.save_to_model:
            Gedcom.objects.create(tree=self.tree, row_num=self.row_num, value=value, used_by_chart=used_by_chart)
            self.row_num += 1
        else:
            self.f.write(value)

    def write_id(self, tag, xref, id=None, used_by_chart=True):
        s_value = '0 ' + self.make_xref(tag, xref, id) + ' ' + tag + '\n'
        self.write_row(s_value, used_by_chart)

    def write_link(self, level, tag, xref, id=None, used_by_chart=True):
        if self.use_xref or (id != None):
            self.write_optional(level, tag, self.make_xref(tag, xref, id), used_by_chart=used_by_chart)

    def write_required(self, level, tag, value='', used_by_chart=True):
        s_value = ''
        if value:
            s_value = ' ' + value
        s_value = str(level) + ' ' + tag + s_value + '\n'
        self.write_row(s_value, used_by_chart)

    def write_optional(self, level, tag, value, used_by_chart=True):
        if value:
            if (type(value) != ChangeDate):
                self.write_row(str(level) + ' ' + tag + ' ' + value + '\n', used_by_chart)
            else:
                date = value.get_date()
                time = value.get_time()
                if date:
                    self.write_row(str(level) + ' DATE ' + date + '\n', used_by_chart)
                    if time:
                        self.write_row(str(level+1) + ' TIME ' + time + '\n', used_by_chart)

    def write_custom(self, level, tag, value, used_by_chart=True):
        if self.custom_fields:
            self.write_optional(level, tag, value, used_by_chart=used_by_chart)

    def write_text(self, level, tag, text, used_by_chart=True):
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
                    self.write_required(level, tag, part, used_by_chart=used_by_chart)
                    first_note = False
                else:
                    if first_line:
                        self.write_required(level+1, 'CONT', part, used_by_chart=used_by_chart)
                    else:
                        self.write_required(level+1, 'CONC', part, used_by_chart=used_by_chart)
                first_line = False

    def write_address(self, level, addr, used_by_chart=True):
        if addr:
            self.write_required(level, 'ADDR', used_by_chart=used_by_chart)
            self.write_optional(level+1, 'ADR1', addr.addr_adr1, used_by_chart=used_by_chart)
            self.write_optional(level+1, 'ADR2', addr.addr_adr2, used_by_chart=used_by_chart)
            self.write_optional(level+1, 'ADR3', addr.addr_adr3, used_by_chart=used_by_chart)
            self.write_optional(level+1, 'CITY', addr.addr_city, used_by_chart=used_by_chart)
            self.write_optional(level+1, 'STAE', addr.addr_stae, used_by_chart=used_by_chart)
            self.write_optional(level+1, 'POST', addr.addr_post, used_by_chart=used_by_chart)
            self.write_optional(level+1, 'CTRY', addr.addr_ctry, used_by_chart=used_by_chart)
            self.write_optional(level, 'PHON', addr.phon, used_by_chart=used_by_chart)
            self.write_optional(level, 'PHON', addr.phon2, used_by_chart=used_by_chart)
            self.write_optional(level, 'PHON', addr.phon3, used_by_chart=used_by_chart)
            self.write_optional(level, 'EMAIL', self.safe(addr.email), used_by_chart=used_by_chart)
            self.write_optional(level, 'EMAIL', self.safe(addr.email2), used_by_chart=used_by_chart)
            self.write_optional(level, 'EMAIL', self.safe(addr.email3), used_by_chart=used_by_chart)
            self.write_optional(level, 'FAX', addr.fax, used_by_chart=used_by_chart)
            self.write_optional(level, 'FAX', addr.fax2, used_by_chart=used_by_chart)
            self.write_optional(level, 'FAX', addr.fax3, used_by_chart=used_by_chart)
            self.write_optional(level, 'WWW', addr.www, used_by_chart=used_by_chart)
            self.write_optional(level, 'WWW', addr.www2, used_by_chart=used_by_chart)
            self.write_optional(level, 'WWW', addr.www3, used_by_chart=used_by_chart)

    def safe(self, value):
        if value:
            return value.replace('@', '@@')

    def write_place(self, level, plac, used_by_chart=True):
        if plac:
            self.write_required(level, 'PLAC', plac.name, used_by_chart=used_by_chart)
            for x in NamePhoneticVariation.objects.filter(plac=plac.id):
                self.write_phonetic(level+1, x, used_by_chart=used_by_chart)
            for x in NameRomanizedVariation.objects.filter(plac=plac.id):
                self.write_romanized(level+1, x, used_by_chart=used_by_chart)
            if (plac.map_lati or plac.map_long):
                self.write_required(level+1, 'MAP', used_by_chart=used_by_chart)
                self.write_optional(level+2, 'LATI', plac.map_lati, used_by_chart=used_by_chart)
                self.write_optional(level+2, 'LONG', plac.map_long, used_by_chart=used_by_chart)
                for x in NoteStructure.objects.filter(plac=plac.id).order_by('_sort'):
                    self.write_note_link(level, x, used_by_chart=used_by_chart)

    def write_note_link(self, level, note_struct, used_by_chart=True):
        if note_struct and note_struct.note:
            if self.use_xref:
                self.write_text(level, 'NOTE', '@N' + str(note_struct.note._sort) + '@', used_by_chart=used_by_chart)
            else:
                self.write_text(level, 'NOTE', '@N' + str(note_struct.note.id) + '@', used_by_chart=used_by_chart)

    def write_chan(self, level, chan, used_by_chart=True):
        if chan:
            self.write_required(level, 'CHAN', used_by_chart=used_by_chart)
            self.write_optional(level+1, 'DATE', chan.date, used_by_chart=used_by_chart)
            self.write_optional(level+2, 'TIME', chan.time, used_by_chart=used_by_chart)

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

    def write_name_pieces(self, level, piec, used_by_chart=True):
        if piec:
            self.write_optional(level, 'NPFX', piec.npfx, used_by_chart=used_by_chart)
            self.write_optional(level, 'GIVN', piec.givn, used_by_chart=used_by_chart)
            self.write_optional(level, 'NICK', piec.nick, used_by_chart=used_by_chart)
            self.write_optional(level, 'SPFX', piec.spfx, used_by_chart=used_by_chart)
            self.write_optional(level, 'SURN', piec.surn, used_by_chart=used_by_chart)
            self.write_optional(level, 'NSFX', piec.nsfx, used_by_chart=used_by_chart)
            self.write_optional(level, 'NPFX', piec.npfx, used_by_chart=used_by_chart)
            self.write_custom(level, '_MARNM', piec._marnm, used_by_chart=used_by_chart)
            for x in NoteStructure.objects.filter(pnpi=piec.id).order_by('_sort'):
                self.write_note_link(level, x, used_by_chart=used_by_chart)
            for x in SourceCitation.objects.filter(pnpi=piec.id).order_by('_sort'):
                self.write_citate(level, x, used_by_chart=used_by_chart)

    def write_phonetic(self, level, phon, used_by_chart=True):
        self.write_required(level, 'FONE', phon.value, used_by_chart=used_by_chart)
        self.write_optional(level+1, 'TYPE', phon.type, used_by_chart=used_by_chart)
        self.write_name_pieces(level+1, phon.piec, used_by_chart=used_by_chart)

    def write_romanized(self, level, roma, used_by_chart=True):
        self.write_required(level, 'ROMN', roma.value, used_by_chart=used_by_chart)
        self.write_optional(level+1, 'TYPE', roma.type, used_by_chart=used_by_chart)
        self.write_name_pieces(level+1, roma.piec, used_by_chart=used_by_chart)

    def write_citate(self, level, cita, used_by_chart=True):
        self.write_link(level, 'SOUR', cita.sour._sort, cita.sour.id, used_by_chart=used_by_chart)
        self.write_optional(level+1, 'PAGE', cita.page, used_by_chart=used_by_chart)
        self.write_optional(level+1, 'EVEN', cita.even_even, used_by_chart=used_by_chart)
        self.write_optional(level+2, 'ROLE', cita.even_role, used_by_chart=used_by_chart)
        if (cita.data_date or cita.data_text):
            self.write_required(level+1, 'DATA', used_by_chart=used_by_chart)
        self.write_optional(level+2, 'DATE', cita.data_date, used_by_chart=used_by_chart)
        self.write_text(level+2, 'TEXT', cita.data_text, used_by_chart=used_by_chart) # TODO: many_to_one
        for x in MultimediaLink.objects.filter(cita=cita.id).order_by('_sort'):
            self.write_media_link(1, x, used_by_chart=used_by_chart)
        for x in NoteStructure.objects.filter(cita=cita.id).order_by('_sort'):
            self.write_note_link(1, x, used_by_chart=used_by_chart)
        self.write_optional(level+1, 'QUAY', cita.quay, used_by_chart=used_by_chart)

    def write_repo_citate(self, level, srci, used_by_chart=True):
        self.write_link(level, 'REPO', srci.repo._sort, srci.repo.id, used_by_chart=used_by_chart)
        self.write_optional(level+1, 'CALN', srci.caln, used_by_chart=used_by_chart)
        self.write_optional(level+2, 'MEDI', srci.caln_medi, used_by_chart=used_by_chart)

    def write_indi_event(self, level, even):
        used_by_chart = even.tag and even.tag in ('BIRT', 'DEAT')
        if not self.light_version or used_by_chart:
            self.write_required(level, even.tag, even.value, used_by_chart=used_by_chart)
            self.write_event_detail(level+1, even.deta, used_by_chart=used_by_chart)
            self.write_optional(level+1, 'AGE',  even.age, used_by_chart=used_by_chart)
            #self.write_child(level, even.famc) # ???
            if even.famc:
                self.write_optional(level+1, 'ADOP', even.adop, used_by_chart=used_by_chart)

    def write_indi_attr(self, level, attr, used_by_chart=True):
        if attr.value and (len(attr.value) > 120):
            self.write_text(level, attr.tag, attr.value, used_by_chart=used_by_chart)
        else:
            self.write_required(level, attr.tag, attr.value, used_by_chart=used_by_chart)
        self.write_event_detail(level+1, attr.deta, used_by_chart=used_by_chart)
        self.write_optional(level+1, 'TYPE', attr.type, used_by_chart=used_by_chart)

    def write_fam_event(self, level, even, used_by_chart=True):
        self.write_required(level, even.tag, even.value, used_by_chart=used_by_chart)
        if even.husb_age:
            self.write_required(level+1, 'HUSB', used_by_chart=used_by_chart)
            self.write_required(level+2, 'AGE', even.husb_age, used_by_chart=used_by_chart)
        if even.wife_age:
            self.write_required(level+1, 'WIFE', used_by_chart=used_by_chart)
            self.write_required(level+2, 'AGE', even.husb_age, used_by_chart=used_by_chart)
        self.write_event_detail(level+1, even.deta, used_by_chart=used_by_chart)

    def write_event_detail(self, level, deta, used_by_chart=True):
        if deta:
            self.write_optional(level, 'TYPE', deta.type, used_by_chart=used_by_chart)
            self.write_optional(level, 'DATE', deta.date, used_by_chart=used_by_chart)
            self.write_place(level, deta.plac, used_by_chart=used_by_chart)
            self.write_address(level, deta.addr, used_by_chart=used_by_chart)
            self.write_optional(level, 'AGNC', deta.agnc, used_by_chart=used_by_chart)
            self.write_optional(level, 'RELI', deta.reli, used_by_chart=used_by_chart)
            self.write_optional(level, 'CAUS', deta.caus, used_by_chart=used_by_chart)
            for x in NoteStructure.objects.filter(even=deta.id).order_by('_sort'):
                self.write_note_link(level, x, used_by_chart=used_by_chart)
            for x in SourceCitation.objects.filter(even=deta.id).order_by('_sort'):
                self.write_citate(level, x, used_by_chart=used_by_chart)
            for x in MultimediaLink.objects.filter(even=deta.id).order_by('_sort'):
                self.write_media_link(level, x, used_by_chart=used_by_chart)

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

    def write_asso_link(self, level, asso, used_by_chart=True):
        self.write_required(level, 'ASSO', '@I' + str(asso.id) + '@', used_by_chart=used_by_chart)
        self.write_optional(level+1, 'RELA', asso.asso_rela, used_by_chart=used_by_chart)
        for x in SourceCitation.objects.filter(asso=asso.id).order_by('_sort'):
            self.write_citate(level+1, x, used_by_chart=used_by_chart)
        for x in NoteStructure.objects.filter(asso=asso.id).order_by('_sort'):
            self.write_note_link(level+1, x, used_by_chart=used_by_chart)

    def write_refn(self, level, refn, used_by_chart=True):
        self.write_optional(level, 'REFN', refn.refn, used_by_chart=used_by_chart)
        self.write_optional(level+1, 'TYPE', refn.type, used_by_chart=used_by_chart)

    def write_media_link(self, level, media, used_by_chart=True):
        if media.obje:
            if self.use_xref:
                self.write_required(level, 'OBJE', '@M' + str(media.obje._sort) + '@', used_by_chart=used_by_chart)
            else:
                self.write_required(level, 'OBJE', '@M' + str(media.obje.id) + '@', used_by_chart=used_by_chart)

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

def gedcom_params(user, str_tree_id: str) -> tuple[int, str]:
    item_id = int(str_tree_id)
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
    return 0, f'Family tree with ID {str_tree_id} not found'

def gedcom_start(user, item_id, task_id) -> dict:
    if FamTreeUser.objects.filter(user_id=user.id, tree_id=item_id, can_view=True).exists():
        mgr = ExpGedcom551(user)
        ret = mgr.make_gedcom(item_id, task_id)
        status = ret.get('result', 'error')
        info = ret.get('info', '')
        if status == 'ok':
            status = 'completed'
            info = str(item_id)
        return {'status': status, 'info': info}
    return {'status':'warning', 'info': f'Family tree with id {item_id} not found'}
