from django.db import models


# Create your models here.
class GraphImage(models.Model):
    key = models.CharField(max_length=50, null=False, blank=False, unique=True)
    image = models.FileField(upload_to="graph_images/")
