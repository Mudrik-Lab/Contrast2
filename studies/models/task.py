from django.db import models
from django.db.models import CASCADE


class TaskType(models.Model):
    name = models.CharField(null=False, blank=False, max_length=30)

    def __str__(self):
        return self.name


class Task(models.Model):
    experiment = models.ForeignKey(null=False, blank=False, to="studies.Experiment",
                                   on_delete=CASCADE,
                                   related_name="tasks")

    type = models.ForeignKey(null=False, blank=False, on_delete=CASCADE,
                             to=TaskType)  # TODO validators from configuration

    def __str__(self):
        return f"experiment: {self.experiment_id}, type {self.type}"

