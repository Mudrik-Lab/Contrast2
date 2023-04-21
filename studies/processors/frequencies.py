from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Subquery, Func
from django.db.models.functions import JSONObject

from studies.choices import InterpretationsChoices, TheoryDrivenChoices
from studies.models import Experiment, Interpretation, FindingTag, Theory
from studies.processors.base import BaseProcessor


class FrequenciesGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        experiments = experiments.filter(finding_tags__family__name="Frequency")
        super().__init__(experiments=experiments, **kwargs)
        self.theory = None

        theory = kwargs.pop("theory", [])
        if len(theory):
            theory_reference = theory[0]
            try:
                theory = Theory.objects.get(name=theory_reference)
            except Theory.DoesNotExist:
                theory = Theory.objects.get(id=theory_reference)
            self.theory = theory

        self.is_theory_driven_only = kwargs.pop("is_theory_driven", [False])[0]
        self.techniques = kwargs.pop("techniques", [])

    def process(self):
        queryset = Interpretation.objects.filter(type=InterpretationsChoices.PRO)
        if self.theory is not None:
            queryset = queryset.filter(theory__parent__name=self.theory)
        experiments_interpretations = queryset\
            .filter(experiment__finding_tags__technique__name__in=self.techniques) \
            .filter(experiment__in=self.experiments)

        if self.is_theory_driven_only:
            experiments_interpretations = experiments_interpretations.filter(
                experiment__theory_driven=TheoryDrivenChoices.DRIVEN)

        experiments = experiments_interpretations  # .values("experiment")

        relevant_finding_tags = FindingTag.objects.select_related("experiment") \
            .prefetch_related("type", "technique") \
            .filter(family__name="Frequency")\
            .filter(technique__name__in=self.techniques)

        finding_tags_subquery_series = relevant_finding_tags \
            .filter(experiment__in=OuterRef("experiment_id")) \
            .order_by("band_lower_bound", "band_higher_bound", "type__name") \
            .annotate(data=JSONObject(start=F("band_lower_bound"), end=F("band_higher_bound"), name=F("type__name"))) \
            .values_list("data")

        order_query = relevant_finding_tags.filter(experiment=OuterRef("experiment_id"))\
            .order_by("band_lower_bound")
        max_order_query = relevant_finding_tags.filter(experiment=OuterRef("experiment_id"))\
            .order_by("band_higher_bound")

        qs = experiments \
            .annotate(min_band_lower=Subquery(order_query.values("band_lower_bound")[:1])) \
            .annotate(max_band_higher=Subquery(max_order_query.values("band_higher_bound")[:1])) \
            .values("experiment_id").annotate(series=ArraySubquery(finding_tags_subquery_series)) \
            .annotate(field_len=Func(F('series'), function='CARDINALITY')) \
            .filter(field_len__gt=self.min_number_of_experiments) \
            .order_by("min_band_lower", "max_band_higher") \
            .distinct() \
            .values("series")

        return qs
