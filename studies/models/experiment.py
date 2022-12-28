from django.db import models
from django.db.models import CASCADE


class Experiment(models.Model):

    study = models.ForeignKey(to="studies.Study", on_delete=CASCADE, related_name="experiments")

