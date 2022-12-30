from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db.models import CASCADE, SET_NULL
from django.db import models
from django_countries.fields import CountryField

from approval_process.choices import ApprovalChoices


# from studies.models.author import Author


class Study(models.Model):
    # TODO should it be through affiliation?
    authors = models.ManyToManyField(to="studies.Author", related_name="studies", )
    name = models.TextField(null=False, blank=False)
    DOI = models.CharField(null=False, blank=False, unique=True, max_length=100)
    title = models.TextField(null=True, blank=True)
    year = models.PositiveIntegerField(null=False, blank=False, validators=[validators.MinValueValidator(1900),
                                                                            validators.MaxValueValidator(2100)])
    corresponding_author_email = models.EmailField(null=False, blank=False)
    approval_process = models.OneToOneField(null=True,
                                            blank=True,
                                            to="approval_process.ApprovalProcess",
                                            on_delete=SET_NULL)
    approval_status = models.IntegerField(choices=ApprovalChoices.choices, null=False, blank=False,
                                          default=ApprovalChoices.PENDING)
    key_words = ArrayField(models.CharField(max_length=50, blank=False, null=False))
    references = models.TextField(null=True, blank=True)
    funding = models.TextField(null=True, blank=True)
    source_title = models.CharField(null=True, blank=True, max_length=200)
    abbreviated_source_title = models.CharField(null=True, blank=True, max_length=200)
    link = models.URLField(null=False, blank=False)
    publisher = models.CharField(null=True, blank=True, max_length=100)
    abstract = models.TextField(null=True, blank=True)
    countries = ArrayField(CountryField(null=False, blank=False)) # Wondering if this is a good modeling, but we'll see
    affiliations = models.TextField(null=False, blank=False)

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        # TODO: add creation of approval process here
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
