from django.db import models
from django.db.models import CASCADE

from studies.choices import TypeOfConsciousnessChoices, ReportingChoices, TheoryDrivenChoices


class Experiment(models.Model):
    """
    This is a major model here, lot's of data "belongs" to the experiment in related models, so the experiment is codified there
    """
    study = models.ForeignKey(to="studies.Study", on_delete=CASCADE, related_name="experiments")
    finding_description = models.CharField(null=False, blank=False, max_length=254)
    # stimuli = models.ManyToManyField(to="studies.Stimulus", related_name="experiments")
    techniques = models.ManyToManyField(to="studies.Technique", related_name="experiments")
    # finding_tags = models.ManyToManyField(to="studies.FindingTag", related_name="experiments")
    interpretations = models.ManyToManyField(to="studies.Theory",
                                             related_name="experiments_interpretations",
                                             through="studies.Interpretation")
    paradigms = models.ManyToManyField(to="studies.Paradigm", related_name="experiments")
    # samples = models.ManyToManyField(to="studies.Sample", related_name="experiments")
    # tasks = models.ManyToManyField(to="studies.Task", related_name="experiments")  # how to show options to None
    consciousness_measures = models.ManyToManyField(to="studies.ConsciousnessMeasure", related_name="experiments") #TODO find out
    type_of_consciousness = models.CharField(null=False, blank=False, choices=TypeOfConsciousnessChoices.choices,
                                             max_length=20)
    is_reporting = models.CharField(null=False, blank=False, choices=ReportingChoices.choices, max_length=20)
    theory_driven = models.CharField(null=False, blank=False, choices=TheoryDrivenChoices.choices, max_length=20)
    theory_driven_theories = models.ManyToManyField(to="studies.Theory",
                                                    related_name="experiments_driven",
                                                    )
    # measures = models.ManyToManyField(to="studies.Measure", related_name="experiments")

    # TODO add all relevant Interpretations on creations

