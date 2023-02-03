from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db.models import CASCADE, SET_NULL
from django.db import models
from django_countries.fields import CountryField
from django.conf import settings
from approval_process.choices import ApprovalChoices


class Study(models.Model):
    class Meta:
        verbose_name_plural = "studies"
    authors = models.ManyToManyField(to="studies.Author", related_name="studies")
    DOI = models.CharField(null=False, blank=False, unique=True, max_length=100)
    title = models.TextField(null=False, blank=False)
    year = models.PositiveIntegerField(null=False, blank=False, validators=[validators.MinValueValidator(1900),
                                                                            validators.MaxValueValidator(2100)])
    corresponding_author_email = models.EmailField(null=False, blank=False)
    approval_process = models.OneToOneField(null=True,
                                            blank=True,
                                            to="approval_process.ApprovalProcess",
                                            on_delete=SET_NULL)
    approval_status = models.IntegerField(choices=ApprovalChoices.choices, null=False, blank=False,
                                          default=ApprovalChoices.PENDING)
    authors_key_words = ArrayField(models.CharField(max_length=50, blank=False, null=False))
    funding = models.TextField(null=True, blank=True)
    source_title = models.CharField(null=True, blank=True, max_length=200)
    abbreviated_source_title = models.CharField(null=True, blank=True, max_length=200)
    countries = ArrayField(CountryField(null=False, blank=False))  # Wondering if this is a good modeling, but we'll see
    affiliations = models.TextField(null=False, blank=False)
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=SET_NULL) #Optional submitter

    def __str__(self):
        return f"{self.id} {self.title}"

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        # TODO: add creation of approval process here
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
