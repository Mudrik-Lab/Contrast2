from django.db import models


class Technique(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)

    def __str__(self):
        return self.name

