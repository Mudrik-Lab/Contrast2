import itertools

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Func, Count
from django.db.models.functions import JSONObject
from studies.models import Experiment,  AggregatedInterpretation
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
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=self.interpretation) \
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
        theory_subquery = filtered_subquery.values("parent_theory_acronyms") \
            .annotate(experiment_count=Count("id", distinct=True))

        if self.is_csv:
            ids = queryset.annotate(experiments=ArraySubquery(filtered_subquery.values_list("experiment_id"))).values_list(
                "experiments", flat=True)
            return set(list(itertools.chain.from_iterable(ids)))

        subquery = theory_subquery \
            .order_by("-experiment_count") \
            .filter(experiment_count__gt=self.min_number_of_experiments) \
            .annotate(data=JSONObject(key=F("parent_theory_acronyms"), value=F("experiment_count"))) \
            .values_list("data")

        qs = queryset \
            .values("series_name").annotate(series=ArraySubquery(subquery)) \
            .annotate(field_len=Func(F('series'), function='CARDINALITY')) \
            .filter(field_len__gt=0) \
            .values("series_name", "series") \
            .order_by("series_name")
        # Note we're filtering out empty timeseries with the cardinality option
        retval = []
        for dataset in list(qs):
            dataset["value"] = self.accumulate_total_from_series(dataset["series"])
            retval.append(dataset)
        return sorted(retval, key=lambda x: x["value"], reverse=True)
