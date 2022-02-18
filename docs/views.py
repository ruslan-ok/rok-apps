from task.const import ROLE_DOC, ROLE_APP
from rusel.base.views import BaseDirListView
from rusel.files import storage_path
from docs.config import app_config

role = ROLE_DOC
app = ROLE_APP[role]

class ListView(BaseDirListView):
    def __init__(self, *args, **kwargs):
        self.template_name = 'docs/folder.html'
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.store_dir = storage_path.format(self.request.user.username) + 'docs/'
        context = super().get_context_data(**kwargs)
        context['list_href'] = '/docs/'
        return context

