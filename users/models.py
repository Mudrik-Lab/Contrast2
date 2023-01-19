import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings

from users.choices import AcademicStageChoices, GenderChoices


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    date_of_birth = models.DateField(null=True, blank=True, validators=[MinValueValidator(datetime.date(1900, 1, 1)),
                                                                        MaxValueValidator(datetime.date(2100, 1, 1))])
    gender = models.CharField(max_length=50, null=True, blank=True, choices=GenderChoices.choices)
    academic_affiliation = models.TextField(null=True, blank=True)
    academic_stage = models.CharField(max_length=50, null=True, blank=True, choices=AcademicStageChoices.choices)

    @classmethod
    def create_profile(cls, user):
        Profile.objects.create(user=user)
    # TODO other user profile attirbutes here
