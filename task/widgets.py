from django.forms.widgets import Input
from django.forms import FileInput
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

class AvatarInput(FileInput):
    input_type = 'file'
    template_name = 'task/avatar.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        #context['categories'] = get_categories_list(value)
        #value = ''
        return context

    def render(self, name, value, attrs=None):

        config.height = self.attrs['height']
        config.width = self.attrs['width']

        context = {}
        context['name'] = name
        context['config'] = config

        context['avatar_url'] = value.url if value else '/static/Default-avatar.jpg'
        context['id'] = attrs.get('id', 'id_' + name)
        # todo fix HACK
        #context['STATIC_URL'] = settings.STATIC_URL
        return render_to_string('task/avatar.html', context)


