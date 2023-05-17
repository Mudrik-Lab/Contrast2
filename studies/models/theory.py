from django.db.models import CASCADE

from django.db import models


class Theory(models.Model):
    class Meta:
        verbose_name_plural = "theories"

    name = models.CharField(null=False, blank=False, max_length=100)
    parent = models.ForeignKey(null=True, blank=True, to="studies.Theory", on_delete=CASCADE, related_name="children")
    acronym = models.CharField(null=True, blank=True, max_length=10)

    def __str__(self):
        if self.parent is not None:
            return f"{self.name} - {self.acronym} child of {self.parent.name}"
        else:
            return f"{self.name} - {self.acronym}"
