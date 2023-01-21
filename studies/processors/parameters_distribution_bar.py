from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Func, Subquery, Count, Sum, IntegerField
from django.db.models.functions import JSONObject

from studies.choices import InterpretationsChoices
from studies.models import Experiment, Paradigm, Interpretation
from studies.processors.base import BaseProcessor


class ParametersDistributionBarGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]
        theory = kwargs.pop("theory")
        self.theory = theory[0]

    def process(self):
        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def process_paradigm_family(self):

        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__paradigms__parent=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = Paradigm.objects.filter(parent__isnull=True).values("name").distinct(
            ).annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, queryset: QuerySet, filtered_subquery: QuerySet):
        # Hopefully this is generic enough to be reused
        by_relation_type_subquery = filtered_subquery.filter(theory__parent=self.theory).filter(
            relation_type__in=[InterpretationsChoices.PRO, InterpretationsChoices.CHALLENGES]).values(
            "relation_type").order_by("-relation_type").annotate(experiment_count=Count("id"))
        subquery = by_relation_type_subquery \
            .annotate(data=JSONObject(key=F("relation_type"), value=F("experiment_count"))) \
            .values_list("data")

        ids_subquery = by_relation_type_subquery \
            .order_by("experiment")\
            .values_list("experiment")

        qs = queryset \
            .values("series_name").annotate(series=ArraySubquery(subquery)) \
            .annotate(ids_list=ArraySubquery(ids_subquery))\
            .annotate(totals=Func(F('ids_list'), function='CARDINALITY'))\
            .annotate(field_len=Func(F('series'), function='CARDINALITY')) \
            .filter(field_len__gt=0) \
            .values("series_name", "series", "totals") \
            .order_by("-totals", "series_name")
        # Note we're filtering out empty timeseries with the cardinality option
        # TODO order by total of inner values
        return qs
