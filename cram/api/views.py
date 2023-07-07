import urllib.parse
from rest_framework import viewsets, permissions, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from cram.api.serializers import CramGroupSerializer, CramPhraseSerializer, CramLangSerializer, CramLangPhraseSerializer
from cram.models import Lang, CramGroup, Phrase, LangPhrase
from task.const import APP_CRAM

class CramGroupViewSet(viewsets.ModelViewSet):
    serializer_class = CramGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None
    queryset = CramGroup.objects.all()

    def get_queryset(self):
       return CramGroup.objects.filter(user=self.request.user.id)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CramPhraseViewSet(viewsets.ModelViewSet):
    serializer_class = CramPhraseSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None
    queryset = Phrase.objects.all()

    def get_queryset(self):
        return Phrase.objects.filter(user=self.request.user.id)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        name = self.request.query_params.get('name', '')
        if name:
            name = urllib.parse.unquote(name)
            LangPhrase.objects.create(phrase=serializer.instance.id, lang='ru', text=name)

    @action(detail=True, methods=['put'])
    def save_all(self, request, pk=None):
        data = request.data
        p_phrase_id = int(data['phraseId'])
        ret = {
            'phraseId': p_phrase_id,
            'langPhrase': [],
        }
        for lang_phrase in data['langPhrase']:
            p_id = int(lang_phrase['id'])
            p_lang = lang_phrase['lang']
            p_text = lang_phrase['text']
            if LangPhrase.objects.filter(id=p_id).exists():
                lp = LangPhrase.objects.filter(id=p_id).get()
                lp.text = p_text
                lp.save()
            else:
                lang = Lang.objects.filter(user=request.user.id, code=p_lang).get()
                phrase = Phrase.objects.filter(user=request.user.id, id=p_phrase_id).get()
                lp = LangPhrase.objects.create(phrase=phrase, lang=lang, text=p_text)
            ret['langPhrase'].append({'id': lp.id, 'lang': lp.lang.code, 'text': lp.text})
        return Response({'result': 'ok', 'data': ret})

class CramLangViewSet(viewsets.ModelViewSet):
    serializer_class = CramLangSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None
    queryset = Lang.objects.all()

    @action(detail=False)
    def check_init(self, request, pk=None):
        Lang.check_init()
        serializer = CramLangSerializer(Lang.objects.all(), context={'request': request})
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CramLangPhraseViewSet(viewsets.ModelViewSet):
    serializer_class = CramLangPhraseSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None
    queryset = LangPhrase.objects.all()
