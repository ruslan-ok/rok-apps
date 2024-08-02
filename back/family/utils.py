import os, requests
from django.conf import settings
from family.models import FamTree, MultimediaRecord, MultimediaFile

def update_media(tree_id):
    updated = 0
    tree = FamTree.objects.filter(id=tree_id).get()
    for mr in MultimediaRecord.objects.filter(tree=tree_id):
        for mf in MultimediaFile.objects.filter(obje=mr.id):
            load_media(tree, mf)
            updated += 1
    return updated

def load_media(tree, mm_file):
    media_path = f'{settings.DJANGO_STORAGE_PATH}/family_tree/{tree.store_name()}'  # Todo: without username?
    fname = mm_file.file.split('/')[-1]
    r = requests.get(mm_file.file, allow_redirects=True)
    if not os.path.exists(media_path):
        os.makedirs(media_path)
    open(media_path + '/' + fname, 'wb+').write(r.content)
