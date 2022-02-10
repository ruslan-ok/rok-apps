from task.const import ROLE_PHOTO, ROLE_APP
from rusel.base.views import BaseDirListView
from rusel.files import storage_path
from photo.config import app_config

role = ROLE_PHOTO
app = ROLE_APP[role]

class ListView(BaseDirListView):

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.template_name = 'photo/folder.html'

    def get_context_data(self, **kwargs):
        self.store_dir = storage_path.format(self.request.user.id) + 'photo/'
        context = super().get_context_data(**kwargs)
        context['list_href'] = '/photo/'
        return context
