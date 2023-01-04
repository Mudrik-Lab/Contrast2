from django.db.models import CASCADE

from django.db import models


class Theory(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)
    parent = models.ForeignKey(null=True, blank=True, to="studies.Theory", on_delete=CASCADE)

    def __str__(self):
        return f"theory {self.name} parent {self.parent and self.parent.name}"
# TODO: data migration to create existing theories