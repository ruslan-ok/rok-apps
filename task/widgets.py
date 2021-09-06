from django.forms.widgets import Input
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




