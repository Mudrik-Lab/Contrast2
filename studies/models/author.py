from django.db import models


class Author(models.Model):
    name = models.CharField(null=False, blank=False, max_length=100)
