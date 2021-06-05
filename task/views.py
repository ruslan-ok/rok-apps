from django.http import HttpResponseRedirect
from rest_framework import viewsets, permissions, renderers
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from rest_framework.response import Response

from rusel.context import get_base_context
from task.models import Group, Task
from task.serializers import TaskGrpSerializer, TaskGrpSimpleSerializer, ATaskSerializer
from task.const import *

class TaskGrpViewSet(viewsets.ModelViewSet):
    serializer_class = TaskGrpSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        return Group.objects.filter(user=self.request.user).order_by('-created')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskGrpSimpleViewSet(viewsets.ModelViewSet):
    serializer_class = TaskGrpSimpleSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        if 'app' in self.request.query_params:
            app = self.request.query_params['app']
            return Group.objects.filter(user=self.request.user, app=app).order_by('-created')
        return Group.objects.filter(user=self.request.user).order_by('-created')
    
class ATaskViewSet(viewsets.ModelViewSet):
    app = 'home'
    view_as_tree = False
    serializer_class = ATaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.TemplateHTMLRenderer, renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]

    def detail_view(self):
        return self.app + '-detail'
    
    def list_view(self):
        return self.app + '-list'
    
    def app_name(self):
        return 'unknown'
    
    def list_name(self):
        return self.app_name() + ' List'
    
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('-created')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def native(self, request):
        return request.accepted_renderer.format != 'html'
    
    def extra_context(self, context):
        pass

    def get_template_name(self):
        if self.view_as_tree:
            return self.app+'/'+self.app+'_tree.html'
        return self.app+'/'+self.app+'_list.html'

    def list(self, request, *args, **kwargs):
        if self.native(request):
            return super(ATaskViewSet, self).list(request, *args, **kwargs)

        context = get_base_context(request, self.app, False, self.app_name())
        self.extra_context(context)
        return Response(context, template_name=self.get_template_name())

    def create(self, request, *args, **kwargs):
        if self.native(request):
            return super(ATaskViewSet, self).create(request, *args, **kwargs)

        serializer = self.get_serializer(data={'name': request.data['item_add-name']})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return HttpResponseRedirect(str(serializer.instance.id) + '/')

    def retrieve(self, request, *args, **kwargs):
        if self.native(request):
            return super(ATaskViewSet, self).retrieve(request, *args, **kwargs)

        context = get_base_context(request, self.app, True, self.app_name())
        self.extra_context(context)
        context['serializer'] = self.get_serializer(self.get_object())
        context['list_url'] = reverse(self.list_view())
        context['list_name'] = self.list_name()
        return Response(context, template_name=self.get_template_name())
    
    def update(self, request, *args, **kwargs):
        if self.native(request):
            return super(ATaskViewSet, self).update(request, *args, **kwargs)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        context = get_base_context(request, self.app, True, self.app_name())
        self.extra_context(context)
        context['serializer'] = serializer
        context['list_url'] = reverse(self.list_view())
        context['list_name'] = self.list_name()
        return Response(context, template_name=self.get_template_name())

    def destroy(self, request, *args, **kwargs):
        if self.native(request):
            return super(ATaskViewSet, self).destroy(request, *args, **kwargs)

        return HttpResponseRedirect(reverse(self.list_view()))

    @action(detail=True, methods=['post'])
    def modify(self, request, pk=None):
        instance = self.get_object()

        if 'item-delete' in request.data:
            instance.delete()
            return HttpResponseRedirect(reverse(self.list_view()))

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return HttpResponseRedirect(reverse(self.detail_view(), args=[instance.id]))

#------------------------------------------------------------------------------

class NoteViewSet(ATaskViewSet):
    app = 'note'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, app_note=NOTE).order_by('-created')

#------------------------------------------------------------------------------

class NewsViewSet(ATaskViewSet):
    app = 'news'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, app_note=NOTE).order_by('-created')


