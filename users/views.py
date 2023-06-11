from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import mixins

from studies.permissions import SelfOnlyProfilePermission
from users.models import Profile
from users.serializers import ProfileSerializer


# Create your views here.

class ProfilesView(GenericViewSet, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    queryset = Profile.objects.all()
    permission_classes = (SelfOnlyProfilePermission, )

    @action(detail=True, methods=["POST"], serializer_class=ProfileSerializer,
            permission_classes=[AllowAny])
    def register(self, request, **kwargs):
        pass
