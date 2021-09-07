from task.models import BaseCustomTask
from task.files import get_files_list
from task.categories import get_categories_list
from task.models import TaskGroup, Urls

class Note(BaseCustomTask):

    def get_info(self):
        ret = []
        
        if not self.grp:
            if TaskGroup.objects.filter(task=self.id).exists():
                ret.append({'text': TaskGroup.objects.filter(task=self.id).get().group.name})

        files = (len(get_files_list(self.user, 'note', 'note', self.id)) > 0)

        links = len(Urls.objects.filter(task=self.id)) > 0
    
        if self.info or links or files:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            if self.info:
                ret.append({'icon': 'notes'})
            if links:
                ret.append({'icon': 'url'})
            if files:
                ret.append({'icon': 'attach'})
    
        if self.categories:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            categs = get_categories_list(self.categories)
            for categ in categs:
                ret.append({'icon': 'category', 'text': categ.name, 'color': 'category-design-' + categ.design})
    
        return ret

