from django.contrib import admin
from task.models import Task, TGroup, TaskView

admin.site.register(Task)
admin.site.register(TGroup)
admin.site.register(TaskView)

