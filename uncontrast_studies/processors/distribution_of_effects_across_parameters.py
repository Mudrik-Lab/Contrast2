import itertools

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Count, Func
from django.db.models.functions import JSONObject
from uncontrast_studies.models import UnConExperiment, UnConSuppressedStimulus, UnConsciousnessMeasure, UnConSample
from uncontrast_studies.processors.base import BaseProcessor


class DistributionOfEffectsAcrossParametersGraphDataProcessor(BaseProcessor):
    """ """

    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("continuous_breakdown")
        self.breakdown = breakdown[0]

    def process(self):
        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def process_suppressed_stimuli_duration(self):
        subquery = UnConSuppressedStimulus.objects.filter(experiment__significance=OuterRef("series_name")).annotate(
            value=F("duration")
        )
        return self._aggregate_query_by_breakdown(subquery)

    def process_number_of_stimuli(self):
        subquery = UnConSuppressedStimulus.objects.filter(experiment__significance=OuterRef("series_name")).annotate(
            value=F("number_of_stimuli")
        )
        return self._aggregate_query_by_breakdown(subquery)

    def process_unconsciousness_measure_number_of_trials(self):
        subquery = UnConsciousnessMeasure.objects.filter(experiment__significance=OuterRef("series_name")).annotate(
            value=F("number_of_trials")
        )
        return self._aggregate_query_by_breakdown(subquery)

    def process_unconsciousness_measure_number_of_participants_in_awareness_test(self):
        subquery = UnConsciousnessMeasure.objects.filter(experiment__significance=OuterRef("series_name")).annotate(
            value=F("number_of_participants_in_awareness_test")
        )
        return self._aggregate_query_by_breakdown(subquery)

    def process_sample_size_included(self):
        subquery = UnConSample.objects.filter(experiment__significance=OuterRef("series_name")).annotate(
            value=F("size_included")
        )
        return self._aggregate_query_by_breakdown(subquery)

    def process_sample_size_excluded(self):
        subquery = UnConSample.objects.filter(experiment__significance=OuterRef("series_name")).annotate(
            value=F("sample_size_excluded")
        )
        return self._aggregate_query_by_breakdown(subquery)

    def _aggregate_query_by_breakdown(self, filtered_subquery):
        # TODO: move the value param to be passed by the breadkdown
        queryset = (
            UnConExperiment.objects.values("significance")
            .distinct("significance")
            .annotate(series_name=F("significance"))
        )

        if self.is_csv:
            ids = queryset.annotate(experiments=ArraySubquery(filtered_subquery.values_list("experiment"))).values_list(
                "experiments", flat=True
            )
            return set(list(itertools.chain.from_iterable(ids)))
        subquery = (
            filtered_subquery.annotate(value=F("value"))
            .values("value")
            .order_by("value")
            .annotate(experiment_count=Count("experiment", distinct=True))
            .annotate(data=JSONObject(year=F("value"), value=F("experiment_count")))
            .values_list("data")
        )

        qs = (
            queryset.values("series_name")
            .annotate(series=ArraySubquery(subquery))  # TODO: sub query always the significance options
            .annotate(field_len=Func(F("series"), function="CARDINALITY"))
            .filter(field_len__gt=0)
            .values("series_name", "series")
            .order_by("series_name")
        )
        # Note we're filtering out empty timeseries with the cardinality option
        return qs
