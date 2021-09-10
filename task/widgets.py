from django.forms.widgets import Input, ClearableFileInput
from task.categories import get_categories_list

class UrlsInput(Input):
    input_type = 'text'
    template_name = 'task/url_input.html'

class CategoriesInput(Input):
    input_type = 'text'
    template_name = 'task/categories.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['categories'] = get_categories_list(value)
        value = ''
        return context

class FileUpload(Input):
    input_type = 'file'
    template_name = 'task/add_file.html'

class AvatarInput(ClearableFileInput):
    input_type = 'file'
    template_name = 'task/avatar.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        #context['categories'] = get_categories_list(value)
        #value = ''
        return context




