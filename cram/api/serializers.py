from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from cram.models import Lang, CramGroup, Phrase, LangPhrase

class GroupNode(serializers.PrimaryKeyRelatedField):

    def to_internal_value(self, data):
        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)
        queryset = self.get_queryset()
        data = data.replace(',', '').replace('.', '')
        try:
            if isinstance(data, bool):
                raise TypeError
            if queryset:
                return queryset.get(pk=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)

class CramGroupSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    node = GroupNode(allow_null=True, queryset=CramGroup.objects.all(), required=False)
    languages = serializers.CharField(source='currency')
    class Meta:
        model = CramGroup
        fields = ['id', 'user', 'node', 'name', 'sort', 'info', 'languages']

class CramPhraseSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    group = GroupNode(allow_null=True, label='Group', queryset=CramGroup.objects.all(), required=False)
    class Meta:
        model = Phrase
        fields = ['id', 'user', 'group', 'sort', 'categories']

class CramLangSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Lang
        fields = ['id', 'user', 'code', 'name']

class CramLangPhraseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LangPhrase
        fields = ['id', 'phrase', 'lang', 'text']

