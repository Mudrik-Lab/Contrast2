from django.db.models import CASCADE

from django.db import models


class Theory(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)
    parent = models.ForeignKey(null=True, blank=True, to="studies.Theory", on_delete=CASCADE)

    def __str__(self):
        if self.parent is not None:
            return f"{self.name} parent {self.parent.name}"
        else:
            return f"{self.name}"
# TODO: data migration to create existing theories