from django.db import models
from django.db.models import CASCADE, PROTECT


class UnConParadigm(models.Model):
    main = models.ForeignKey(
        null=True, blank=True, related_name="specific_paradigm", to="uncontrast_studies.UnConParadigm", on_delete=PROTECT
    )
    name = models.CharField(null=False, blank=False, max_length=100)
class UnConSuppressionMethod(models.Model):
    experiment = models.ForeignKey(
        null=False, blank=False, to="uncontrast_studies.UnConExperiment", on_delete=CASCADE, related_name="suppression_methods"
    )
    paradigms = models.ManyToManyField("uncontrast_studies.UnConParadigm", related_name="suppression_methods")