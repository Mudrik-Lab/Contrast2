from django.contrib.auth import get_user_model
from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.utils import model_meta

from users.models import Profile


class UsernameOnlySerializer(serializers.Serializer):
    username = serializers.CharField()


class UserResponseSerializer(serializers.Serializer):
    exists = serializers.BooleanField()


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    token = serializers.CharField()


class PasswordResetResponseSerializer(serializers.Serializer):
    password_reset = serializers.BooleanField()


class RequestPasswordResetResponseSerializer(serializers.Serializer):
    reset_requested = serializers.BooleanField()


class ProfileUpdateSerializer(serializers.ModelSerializer):
    user = PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    country_of_residence = CountryField(required=False)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(required=False)

    class Meta:
        model = Profile
        fields = (
            "id", "user", "date_of_birth", "self_identified_gender", "academic_affiliation", "country_of_residence",
            "academic_stage", "has_ASSC_membership", "username", "email")

    def update(self, instance, validated_data):
        info = model_meta.get_field_info(instance)
        user_properties = ["email"]
        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        user_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))

            else:
                if attr in user_properties:
                    user_fields.append((attr, value))
                setattr(instance, attr, value)

        instance.save()

        if len(user_fields):
            for attr, value in user_fields:
                setattr(instance.user, attr, value)
            instance.user.save()

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance


class ProfileSerializer(serializers.ModelSerializer):
    user = PrimaryKeyRelatedField(read_only=True)
    country_of_residence = CountryField(required=False)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id", "user", "date_of_birth", "self_identified_gender", "academic_affiliation", "country_of_residence",
            "academic_stage", "has_ASSC_membership", "username", "email")


class ProfileCreateSerializer(ProfileSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("username", "password", "email")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "username")
