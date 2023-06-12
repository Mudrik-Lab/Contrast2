from django.contrib.auth import get_user_model
from django.core.exceptions import BadRequest
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import mixins

from studies.permissions import SelfOnlyProfilePermission
from users.models import Profile
from users.serializers import ProfileSerializer, RegistrationSerializer


# Create your views here.

class ProfilesView(GenericViewSet, mixins.UpdateModelMixin):
    queryset = Profile.objects.all()
    permission_classes = (SelfOnlyProfilePermission,)
    serializer_class = ProfileSerializer

    @extend_schema(request=RegistrationSerializer)
    @action(detail=False, methods=["POST"],
            permission_classes=[AllowAny])
    def register(self, request, **kwargs):
        UserModel = get_user_model()

        serializer = RegistrationSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)

        if UserModel.objects.filter(username=serializer.validated_data.get("username")).exists():
            raise BadRequest()

        user = UserModel.objects.create_user(username=serializer.validated_data.get("username"),
                                             password=serializer.validated_data.get("password"),
                                             email=serializer.validated_data.get("email"))
        profile_data = dict(user=user.id, **request.data)
        profile_serializer = self.get_serializer(data=profile_data)
        profile_serializer.is_valid(raise_exception=True)
        profile_serializer.save()

        return Response(profile_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["GET"], permission_classes=[permissions.IsAuthenticated])
    def home(self, request, **kwargs):
        user = request.user
        serializer = self.get_serializer(instance=user.profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
