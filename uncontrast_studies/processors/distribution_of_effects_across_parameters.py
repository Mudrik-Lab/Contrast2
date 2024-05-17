import itertools

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Count, Func, IntegerField
from django.db.models.functions import JSONObject, Cast, Floor, Ceil
from uncontrast_studies.models import UnConExperiment, UnConSuppressedStimulus, UnConsciousnessMeasure, UnConSample, \
    UnConFinding
from uncontrast_studies.processors.base import BaseProcessor


class DistributionOfEffectsAcrossParametersGraphDataProcessor(BaseProcessor):
    """ """

    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("continuous_breakdown")
        self.breakdown = breakdown[0]
        self.bin_size = int(kwargs.pop("bin_size", ["1"])[0])

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

    def process_outcome_number_of_trials(self):
        subquery = UnConFinding.objects.filter(experiment__significance=OuterRef("series_name")).annotate(
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
            value=F("size_excluded")
        )
        return self._aggregate_query_by_breakdown(subquery)

    def _aggregate_query_by_breakdown(self, filtered_subquery):
        BIN_SIZE = 10
        BIN_NUMBER = 10
        # TODO: move the value param to be passed by the breadkdown
        queryset = ( # This is for each kind of significance
            UnConExperiment.objects.values("significance")
            .distinct("significance")
            .annotate(series_name=F("significance"))
        )

        if self.is_csv:
            ids = queryset.annotate(experiments=ArraySubquery(filtered_subquery.values_list("experiment"))).values_list(
                "experiments", flat=True
            )
            return set(list(itertools.chain.from_iterable(ids)))
        subquery = ( # this is the actual histogram for a specific significance
            filtered_subquery.annotate(value=F("value")).annotate(total=Count("value"))
            .annotate(bin_value=Cast(Floor(F("value")/self.bin_size) * self.bin_size, output_field=IntegerField()))
            .values("bin_value")
            .order_by("bin_value")
            .annotate(experiment_count=Count("experiment", distinct=True))
            .annotate(data=JSONObject(key=F("bin_value"), value=F("experiment_count")))
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
