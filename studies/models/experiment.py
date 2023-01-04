from django.db import models
from django.db.models import CASCADE

from studies.choices import TypeOfConsciousnessChoices, ReportingChoices, TheoryDrivenChoices


class Experiment(models.Model):
    """
    This is a major model here, lots of data "belongs" to the experiment in related models, so the experiment is codified there
    """
    study = models.ForeignKey(to="studies.Study", on_delete=CASCADE, related_name="experiments")
    finding_description = models.TextField(null=False, blank=False)
    techniques = models.ManyToManyField(to="studies.Technique", related_name="experiments") #validator at least one
    interpretations = models.ManyToManyField(to="studies.Theory",
                                             related_name="experiments_interpretations",
                                             through="studies.Interpretation")
    paradigms = models.ManyToManyField(to="studies.Paradigm", related_name="experiments")  #validator at least one
    type_of_consciousness = models.CharField(null=False, blank=False, choices=TypeOfConsciousnessChoices.choices,
                                             max_length=20)
    is_reporting = models.CharField(null=False, blank=False, choices=ReportingChoices.choices, max_length=20)
    theory_driven = models.CharField(null=False, blank=False, choices=TheoryDrivenChoices.choices, max_length=20)
    theory_driven_theories = models.ManyToManyField(to="studies.Theory",
                                                    related_name="experiments_driven",
                                                    )

    # TODO add all relevant Interpretations on creations

    def __str__(self):
        return f"study {self.study_id}, id {self.id}"

