from django.db import models
from django.db.models import CASCADE

from studies.choices import InterpretationsChoices


class Interpretation(models.Model):
    experiment = models.ForeignKey(to="studies.Experiment", on_delete=CASCADE, related_name="theories")
    theory = models.ForeignKey(to="studies.Theory", on_delete=CASCADE, related_name="experiments")
    type = models.CharField(null=False, blank=False, choices=InterpretationsChoices.choices, max_length=30)

    def __str__(self):
        return f"experiment: {self.experiment_id} theory {self.theory}, type {self.type}"
