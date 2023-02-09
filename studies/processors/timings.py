from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, Subquery, OuterRef, Count, F
from django.db.models.functions import JSONObject

from studies.choices import TheoryDrivenChoices, InterpretationsChoices
from studies.models import Experiment, FindingTag, Interpretation
from studies.processors.base import BaseProcessor


class TimingsGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        sort_first = kwargs.pop("sort_first", ["earliest"])
        self.sort_first = sort_first[0]
        self.theory = kwargs.pop("theory")[0]
        self.is_theory_driven_only = kwargs.pop("is_theory_driven", [False])[0]
        self.tags_types = kwargs.pop("tags_types", [])
        self.techniques = kwargs.pop("techniques", [])

    def process(self):
        experiments_interpretations = Interpretation.objects.filter(theory__parent__name=self.theory,
                                                                    type=InterpretationsChoices.PRO) \
            .filter(experiment__finding_tags__technique__name__in=self.techniques) \
            .filter(experiment__finding_tags__type__name__in=self.tags_types)\
            .filter(experiment__in=self.experiments)

        if self.is_theory_driven_only:
            experiments_interpretations = experiments_interpretations.filter(
                experiment__theory_driven=TheoryDrivenChoices.DRIVEN)

        experiments = experiments_interpretations.values("experiment")

        relevant_finding_tags = FindingTag.objects \
            .select_related("experiment") \
            .prefetch_related("type", "technique") \
            .filter(experiment__in=OuterRef("pk")) \
            .filter(type__name__in=self.tags_types) \
            .filter(technique__name__in=self.techniques) \
            .annotate(data=JSONObject(start=F("onset"), end=F("offset"), name=F("type__name"))) \
            .values_list("data")

        qs = experiments \
            .values("id").annotate(series=ArraySubquery(relevant_finding_tags)).values("series")
        # TODO: filter out empty series
        # TODO: sort by order
        return qs
