from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, Subquery, OuterRef, F, Func
from django.db.models.functions import JSONObject

from contrast_api.choices import TheoryDrivenChoices, InterpretationsChoices
from studies.models import Experiment, FindingTag, Interpretation, Theory
from studies.processors.base import BaseProcessor


class TimingsGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        sort_first = kwargs.pop("sort_first", ["earliest"])
        self.sort_first = sort_first[0]
        theory = kwargs.pop("theory", [])
        self.theory = None
        if len(theory):
            theory_reference = theory[0]
            try:
                theory = Theory.objects.get(name=theory_reference)
            except Theory.DoesNotExist:
                theory = Theory.objects.get(id=theory_reference)
            self.theory = theory
        self.is_theory_driven_only = kwargs.pop("is_theory_driven", [False])[0]
        self.tags_types = kwargs.pop("tags_types", [])
        self.techniques = kwargs.pop("techniques", [])

    def process(self):
        queryset = Interpretation.objects.filter(type=InterpretationsChoices.PRO)
        if self.theory is not None:
            queryset = queryset.filter(theory__parent=self.theory)
        experiments_interpretations = (
            queryset.filter(experiment__finding_tags__technique__name__in=self.techniques)
            .filter(experiment__finding_tags__type__name__in=self.tags_types)
            .filter(experiment__finding_tags__is_NCC=True)
            .filter(experiment__in=self.experiments)
        )

        if self.is_theory_driven_only:
            experiments_interpretations = experiments_interpretations.filter(
                experiment__theory_driven=TheoryDrivenChoices.DRIVEN
            )

        experiments = experiments_interpretations  # .values("experiment")

        relevant_finding_tags = (
            FindingTag.objects.select_related("experiment", "type", "family", "technique")
            .filter(family__name="Temporal")
            .filter(is_NCC=True)
            .filter(type__name__in=self.tags_types)
            .filter(technique__name__in=self.techniques)
        )

        if self.is_csv:
            ids = relevant_finding_tags.filter(
                experiment__in=experiments_interpretations.values_list("experiment_id", flat=True)
            ).values_list("experiment_id", flat=True)
            return set(ids)

        finding_tags_subquery_series = (
            relevant_finding_tags.filter(experiment__in=OuterRef("experiment_id"))
            .order_by("onset", "type__name")
            .annotate(data=JSONObject(start=F("onset"), end=F("offset"), name=F("type__name")))
            .values_list("data")
        )

        order_query = relevant_finding_tags.filter(experiment=OuterRef("experiment_id")).order_by("onset")

        qs = (
            experiments.annotate(min_onset=Subquery(order_query.values("onset")[:1]))
            .values("experiment_id")
            .annotate(series=ArraySubquery(finding_tags_subquery_series))
            .annotate(field_len=Func(F("series"), function="CARDINALITY"))
            .filter(field_len__gt=0)
            .order_by("min_onset")
            .distinct()
            .values("series")
        )
        # TODO implement custom sort using union of two querysets
        return qs
