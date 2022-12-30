from django.db import models

class ConsciousnessMeasure(models.Model):
    class Meta:
        unique_together = [] # ?
    phase = models.CharField(blank=False, null=False, max_length=30)
    type = models.CharField(blank=False, null=False, max_length=30)
