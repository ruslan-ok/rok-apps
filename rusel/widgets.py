from django.forms import widgets
from django.db.models.fields.files import ImageFieldFile
from rusel.categories import get_categories_list

class UrlsInput(widgets.Input):
    input_type = 'text'
    template_name = 'widgets/url_input.html'

class CategoriesInput(widgets.Input):
    input_type = 'text'
    template_name = 'widgets/categories.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['categories'] = get_categories_list(value)
        value = ''
        return context

class FileUpload(widgets.Input):
    input_type = 'file'
    template_name = 'widgets/add_file.html'

class AvatarInput(widgets.FileInput):
    input_type = 'file'
    template_name = 'widgets/avatar.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['avatar_url'] = value.url if value and type(value) == ImageFieldFile else '/static/Default-avatar.jpg'
        return context

class CheckboxInput(widgets.CheckboxInput):
    input_type = 'checkbox'
    template_name = 'widgets/checkbox.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({'wrap_label': False})
        if ('label' not in context['widget']['attrs']):
            context['widget']['attrs'].update({'label': name})
        return context

class SwitchInput(widgets.CheckboxInput):
    input_type = 'checkbox'
    template_name = 'widgets/switch.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({'wrap_label': False})
        if ('label' not in context['widget']['attrs']):
            context['widget']['attrs'].update({'label': name})
        return context

class DateInput(widgets.DateInput):
    input_type = 'date'
    template_name = 'widgets/date.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context

class DateTimeInput(widgets.DateTimeInput):
    input_type = 'datetime-local'
    template_name = 'widgets/datetime.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context

class Select(widgets.Select):
    input_type = 'select'
    template_name = 'widgets/select.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context

class NumberInput(widgets.Input):
    input_type = 'number'
    template_name = 'widgets/input.html'

    def get_context(self, name, value, attrs):
        if (value == None):
            value = 0
        context = super().get_context(name, value, attrs)
        return context

class CompletedInput(widgets.CheckboxInput):
    input_type = 'checkbox'
    template_name = 'widgets/completed.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({'wrap_label': False})
        return context

class EntryUsernameInput(widgets.Input):
    input_type = 'text'
    template_name = 'widgets/entry_username.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context

class EntryValueInput(widgets.Input):
    input_type = 'text'
    template_name = 'widgets/entry_value.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context

class NegativeNumberInput(widgets.Input):
    input_type = 'number'
    template_name = 'widgets/negative_number.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context
