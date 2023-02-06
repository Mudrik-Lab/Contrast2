from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import CASCADE, Q

from studies.choices import TypeOfConsciousnessChoices, ReportingChoices, TheoryDrivenChoices, ExperimentTypeChoices


class Experiment(models.Model):
    """
    This is a major model here, lots of data "belongs" to the experiment in related models, so the experiment is codified there
    """
    class Meta:
        ordering = ["id"]
    study = models.ForeignKey(to="studies.Study", on_delete=CASCADE, related_name="experiments")
    finding_description = models.TextField(null=False, blank=False)
    techniques = models.ManyToManyField(to="studies.Technique", related_name="experiments")  # validator at least one
    interpretations = models.ManyToManyField(to="studies.Theory",
                                             related_name="experiments_interpretations",
                                             limit_choices_to=Q(parent__isnull=False),
                                             through="studies.Interpretation")
    paradigms = models.ManyToManyField(to="studies.Paradigm", related_name="experiments",
                                       limit_choices_to=Q(parent__isnull=False))  # validator at least one
    type_of_consciousness = models.CharField(null=False, blank=False, choices=TypeOfConsciousnessChoices.choices,
                                             max_length=20)
    is_reporting = models.CharField(null=False, blank=False, choices=ReportingChoices.choices, max_length=20)
    theory_driven = models.CharField(null=False, blank=False, choices=TheoryDrivenChoices.choices, max_length=20)
    theory_driven_theories = models.ManyToManyField(to="studies.Theory",
                                                    related_name="experiments_driven",
                                                    limit_choices_to=Q(parent__isnull=False),

                                                    )
    type = models.PositiveIntegerField(null=False, blank=False, choices=ExperimentTypeChoices.choices)

    # TODO add all relevant Interpretations on creations

    def clean(self):
        if len(self.paradigms) == 0 or self.paradigms is None:
            raise ValidationError({"paradigms": "There should be at least one"})
        if len(self.techniques) == 0 or self.techniques is None:
            raise ValidationError({"techniques": "There should be at least one"})

    def __str__(self):
        return f"study {self.study_id}, id {self.id}"
