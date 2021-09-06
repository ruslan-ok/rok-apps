from django.forms.widgets import Input
from task.categories import get_categories_list

class UrlsInput(Input):
    input_type = 'text'
    template_name = 'task/urls.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['urls'] = [{'href':'https://rusel.by', 'name': 'rusel.by'}, {'href':'https://google.com', 'name': 'google.com'}, ]
        return context

class CategoriesInput(Input):
    input_type = 'text'
    template_name = 'task/categories.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['categories'] = get_categories_list(value)
        value = ''
        return context




