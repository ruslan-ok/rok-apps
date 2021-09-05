from django.forms.widgets import Input

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

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['categories'] = [{'href':'https://rusel.by', 'name': 'rusel.by'}, {'href':'https://google.com', 'name': 'google.com'}, ]
        return context




