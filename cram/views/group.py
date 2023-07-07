from django.contrib.auth.mixins import LoginRequiredMixin
from core.views import BaseGroupView
from task.const import ROLE_CRAM
from cram.config import app_config

role = ROLE_CRAM


class GroupView(LoginRequiredMixin, BaseGroupView):

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
