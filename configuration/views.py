from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet

from studies.models import Study


# Create your views here.


class ConfigurationView(GenericViewSet):
    queryset = Study.objects.none()
    permission_classes = (AllowAny,)

    @action(detail=False, methods=["GET"], permission_classes=[AllowAny])
    def studies_creation(self, request, **kwargs):
        pass
