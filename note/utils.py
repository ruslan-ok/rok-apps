from django.shortcuts import get_object_or_404

from hier.models import Folder

#----------------------------------
# Поиск списка "Готово" на текущем уровне
#----------------------------------
def get_ready_folder(user_id, note_file_id):
    note_file = get_object_or_404(Folder.objects.filter(user = user_id, id = note_file_id))
    list_file = get_object_or_404(Folder.objects.filter(user = user_id, id = note_file.node))
    if (list_file.name == 'Готово'):
        return list_file
    
    for list in Folder.objects.filter(user = user_id, node = list_file.node):
        if (list.name == 'Готово'):
            return list

    return None


