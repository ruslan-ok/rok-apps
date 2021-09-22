from django.forms.widgets import Input
from django.forms import FileInput
from django.db.models.fields.files import ImageFieldFile
from task.categories import get_categories_list

class UrlsInput(Input):
    input_type = 'text'
    template_name = 'widgets/url_input.html'

class CategoriesInput(Input):
    input_type = 'text'
    template_name = 'widgets/categories.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['categories'] = get_categories_list(value)
        value = ''
        return context

class FileUpload(Input):
    input_type = 'file'
    template_name = 'widgets/add_file.html'

class AvatarInput(FileInput):
    input_type = 'file'
    template_name = 'widgets/avatar.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['avatar_url'] = value.url if value and type(value) == ImageFieldFile else '/static/Default-avatar.jpg'
        return context

