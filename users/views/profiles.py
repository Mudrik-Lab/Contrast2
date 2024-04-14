from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import BadRequest
import urllib.parse

from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.viewsets import mixins

from contrast_api.application_services.notifier import NotifierService
from contrast_api.studies.permissions import SelfOnlyProfilePermission

from users.models import Profile
from users.serializers import (
    ProfileSerializer,
    UsernameOnlySerializer,
    UserResponseSerializer,
    ProfileUpdateSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    ProfileCreateSerializer,
    RequestPasswordResetSerializer,
    RequestPasswordResetResponseSerializer,
    PasswordResetSerializer,
    PasswordResetResponseSerializer,
)


# Create your views here.


class ProfilesView(GenericViewSet, mixins.UpdateModelMixin):
    queryset = Profile.objects.all()
    permission_classes = (SelfOnlyProfilePermission,)
    serializer_class = ProfileSerializer

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ProfileUpdateSerializer
        elif self.action in ["register"]:
            return ProfileCreateSerializer
        else:
            return super().get_serializer_class()

    @extend_schema(request=UsernameOnlySerializer)
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny], serializer_class=UserResponseSerializer)
    def check_username(self, request, **kwargs):
        """
        Part of the login/register flow
        """
        serializer = UsernameOnlySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        UserModel = get_user_model()
        already_exists = UserModel.objects.filter(username=username).exists()

        res = dict(exists=already_exists)
        serializer = self.get_serializer(data=res)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=UserRegistrationSerializer)
    @action(detail=False, methods=["POST"], permission_classes=[AllowAny], serializer_class=UserSerializer)
    def register_user(self, request, **kwargs):
        UserModel = get_user_model()

        serializer = UserRegistrationSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        if UserModel.objects.filter(
            Q(username=serializer.validated_data.get("username")) | Q(email=serializer.validated_data.get("email"))
        ).exists():
            raise BadRequest("Attempting to register an existing user/email")
        user = UserModel.objects.create_user(
            username=serializer.validated_data.get("username"),
            password=serializer.validated_data.get("password"),
            email=serializer.validated_data.get("email"),
        )
        Profile.create_profile(user=user)
        user_serializer = self.get_serializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, **kwargs):
        if not Profile.objects.filter(user=request.user).exists():
            profile_data = dict(user=request.user.id, **request.data)
            profile_serializer = self.get_serializer(data=profile_data)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
        else:
            instance = request.user.profile
            profile_serializer = ProfileUpdateSerializer(instance, data=request.data, partial=True)
            profile_serializer.is_valid(raise_exception=True)
            self.perform_update(profile_serializer)

            if getattr(instance, "_prefetched_objects_cache", None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

        return Response(profile_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["GET"], permission_classes=[permissions.IsAuthenticated])
    def home(self, request, **kwargs):
        user = request.user
        serializer = self.get_serializer(instance=user.profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=RequestPasswordResetSerializer, responses=RequestPasswordResetResponseSerializer)
    @action(detail=False, methods=["POST"], permission_classes=(AllowAny,))
    def request_password_reset(self, request):
        email = request.data["email"]
        try:
            user = get_user_model().objects.get(email__iexact=email)
            token = urllib.parse.quote_plus(PasswordResetTokenGenerator().make_token(user))
        except get_user_model().DoesNotExist:
            serializer = RequestPasswordResetResponseSerializer(instance={"reset_requested": True})
            # The rationale for this is that we don't want different behavior exposing for frontend if the user exists or not
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        notifier_service = NotifierService()
        try:
            notifier_service.notify_reset_password_request(request=request, recipient=email, user=user, token=token)
            serializer = RequestPasswordResetResponseSerializer(instance={"reset_requested": True})

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            serializer = RequestPasswordResetResponseSerializer(instance={"reset_requested": False})
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request=PasswordResetSerializer, responses=PasswordResetResponseSerializer)
    @action(detail=False, methods=["POST"], permission_classes=(AllowAny,))
    def reset_password(self, request):
        email = request.data["email"]
        password = request.data["password"]
        token = request.data["token"]
        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            serializer = PasswordResetResponseSerializer(instance={"password_reset": False})
            return Response(serializer.data, status=status.HTTP_200_OK)

        res = PasswordResetTokenGenerator().check_token(user=user, token=token)

        if res:
            user.set_password(password)
            user.save()
            serializer = PasswordResetResponseSerializer(instance={"password_reset": True})

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            serializer = PasswordResetResponseSerializer(instance={"password_reset": False})

            return Response(serializer.data, status=status.HTTP_200_OK)
