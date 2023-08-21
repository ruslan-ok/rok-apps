from rest_framework import viewsets, permissions, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from task.const import *
from apart.models import Apart, ApartMeter, ApartService
from apart.api.serializers import *
from apart.multi_currency import multi_currency_init

class ApartView(viewsets.ModelViewSet):
    serializer_class = ApartSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        return Apart.objects.filter(user=self.request.user.id, app_apart=NUM_ROLE_APART).order_by('sort')

    @action(detail=False)
    def multi_currency_init(self, request, pk=None):
        ret = multi_currency_init(request.user)
        return Response(ret)

class ApartMeterView(viewsets.ModelViewSet):
    serializer_class = ApartMeterSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        return ApartMeter.objects.filter(user=self.request.user.id, app_apart=NUM_ROLE_METER_PROP).order_by('-created')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ApartServiceView(viewsets.ModelViewSet):
    serializer_class = ApartServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        return ApartService.objects.filter(user=self.request.user.id, app_apart=NUM_ROLE_SERV_PROP).order_by('-created')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PeriodMetersView(viewsets.ModelViewSet):
    serializer_class = PeriodMetersSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        return PeriodMeters.objects.filter(user=self.request.user.id, app_apart=NUM_ROLE_METER).order_by('-start')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MeterValueView(viewsets.ModelViewSet):
    serializer_class = MeterValueSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        return MeterValue.objects.filter(user=self.request.user.id, app_apart=NUM_ROLE_METER_VALUE)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PeriodServicesView(viewsets.ModelViewSet):
    serializer_class = PeriodServicesSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        return PeriodServices.objects.filter(user=self.request.user.id, app_apart=NUM_ROLE_BILL).order_by('-start')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ServiceAmountView(viewsets.ModelViewSet):
    serializer_class = ServiceAmountSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        return ServiceAmount.objects.filter(user=self.request.user.id, app_apart=NUM_ROLE_SERV_VALUE)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

