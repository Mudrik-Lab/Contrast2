import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings
from django_countries.fields import CountryField

from users.choices import AcademicStageChoices, GenderChoices


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        validators=[MinValueValidator(datetime.date(1900, 1, 1)), MaxValueValidator(datetime.date(2100, 1, 1))],
    )
    self_identified_gender = models.CharField(max_length=50, null=True, blank=True, choices=GenderChoices.choices)
    academic_affiliation = models.TextField(null=True, blank=True)
    country_of_residence = CountryField(null=True, blank=True)
    academic_stage = models.CharField(max_length=50, null=True, blank=True, choices=AcademicStageChoices.choices)
    has_ASSC_membership = models.BooleanField(null=True, blank=True)
    has_opted_for_contrast_updates = models.BooleanField(null=False, blank=False, default=True)
    is_reviewer = models.BooleanField(null=False, blank=False, default=False)

    @staticmethod
    def create_profile(user, **kwargs):
        data = dict(user=user, **kwargs)
        return Profile.objects.create(**data)
