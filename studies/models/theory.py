from django.db.models import CASCADE

from django.db import models


class Theory(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)
    parent = models.ForeignKey(null=True, blank=True, to="studies.Theory", on_delete=CASCADE)

# TODO: data migration to create existing theories