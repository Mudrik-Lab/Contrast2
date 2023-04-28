from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Func, Subquery, Count, Sum, IntegerField, Q
from django.db.models.functions import JSONObject

from contrast_api.orm_helpers import SubqueryCount
from studies.choices import InterpretationsChoices
from studies.models import Experiment, Paradigm, Interpretation, Sample, FindingTagType, FindingTagFamily, TaskType, \
    ModalityType, ConsciousnessMeasurePhaseType, ConsciousnessMeasureType, Technique, MeasureType
from studies.models.stimulus import StimulusCategory
from studies.processors.base import BaseProcessor


class TheoryDrivenDistributionPieGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        interpretation = kwargs.pop("interpretation")
        self.interpretation = interpretation[0]

    def process(self):
        process_func = getattr(self, f"process_theory_driven")
        return process_func()

    def process_theory_driven(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=self.interpretation) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__theory_driven=OuterRef("series_name"))

        breakdown_query = Experiment.objects.values("theory_driven") \
            .distinct() \
            .annotate(series_name=F("theory_driven"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, queryset: QuerySet, filtered_subquery: QuerySet):
        """
        filtered_subquery -> Interpretations filtered
        """
        theory_subquery = filtered_subquery.values("theory__parent__name") \
            .annotate(experiment_count=Count("id", distinct=True))

        subquery = theory_subquery \
            .order_by("-experiment_count") \
            .annotate(data=JSONObject(key=F("theory__parent__name"), value=F("experiment_count"))) \
            .values_list("data")

        ids_subquery = theory_subquery \
            .order_by("experiment") \
            .values_list("experiment_id")

        qs = queryset \
            .values("series_name").annotate(series=ArraySubquery(subquery)) \
            .annotate(field_len=Func(F('series'), function='CARDINALITY')) \
            .annotate(value=SubqueryCount(ids_subquery)) \
            .filter(field_len__gt=0) \
            .filter(value__gt=self.min_number_of_experiments) \
            .values("series_name", "series", "value") \
            .order_by("-value", "series_name")
        # Note we're filtering out empty timeseries with the cardinality option
        # TODO order by total of inner values
        return qs
