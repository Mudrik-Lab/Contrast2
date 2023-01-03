from django.db import models
from django.db.models import SET_NULL


class Paradigm(models.Model):
    parent = models.ForeignKey(null=True,
                               blank=True,
                               related_name="child_paradigm", to="studies.Paradigm",
                               on_delete=SET_NULL)
    name = models.CharField(null=False, blank=False, max_length=100)

# TODO: data migration to create existing paradigms