import itertools

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Count, Func
from django.db.models.functions import JSONObject

from uncontrast_studies.models import (
    UnConExperiment,
    UnConMainParadigm,
    UnConSample,
    UnConProcessingMainDomain,
    UnConSuppressionMethod,
    UnConTaskType,
    UnConModalityType,
    UnConsciousnessMeasurePhase,
    UnConsciousnessMeasureType,
    UnConStimulusCategory,
    UnConSuppressionMethodType,
)
from studies.models.stimulus import StimulusCategory
from uncontrast_studies.processors.base import BaseProcessor


class TrendsOverYearsGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]

    def process(self):
        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def process_paradigm(self):
        experiments_subquery_by_breakdown = self.experiments.filter(paradigm__main=OuterRef("pk"))

        breakdown_query = UnConMainParadigm.objects.values("name").distinct("name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_population(self):
        experiments_subquery_by_breakdown = self.experiments.filter(samples__type=OuterRef("type"))

        breakdown_query = UnConSample.objects.values("type").distinct().annotate(series_name=F("type"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_target_same_as_suppressed_stimulus(self):
        experiments_subquery_by_breakdown = self.experiments.filter(
            is_target_same_as_suppressed_stimulus=OuterRef("series_name")
        )

        breakdown_query = (
            UnConExperiment.objects.values("is_target_same_as_suppressed_stimulus")
            .distinct("is_target_same_as_suppressed_stimulus")
            .annotate(series_name=F("is_target_same_as_suppressed_stimulus"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_task(self):
        experiments_subquery_by_breakdown = self.experiments.filter(tasks__type=OuterRef("pk"))

        breakdown_query = UnConTaskType.objects.values("name").distinct("name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_processing_domain(self):
        experiments_subquery_by_breakdown = self.experiments.filter(experiment__processing_domains__main=OuterRef("pk"))

        breakdown_query = (
            UnConProcessingMainDomain.objects.values("name").distinct("name").annotate(series_name=F("name"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppression_method(self):
        experiments_subquery_by_breakdown = self.experiments.filter(suppression_methods__type=OuterRef("pk"))

        breakdown_query = (
            UnConSuppressionMethodType.objects.values("name").distinct("name").annotate(series_name=F("name"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_category(self):
        experiments_subquery_by_breakdown = self.experiments.filter(suppressed_stimuli__category=OuterRef("pk"))

        breakdown_query = UnConStimulusCategory.objects.values("name").distinct("name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_modality(self):
        experiments_subquery_by_breakdown = self.experiments.filter(suppressed_stimuli__modality=OuterRef("pk"))

        breakdown_query = UnConModalityType.objects.values("name").distinct("name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_category(self):
        experiments_subquery_by_breakdown = self.experiments.filter(target_stimuli__category=OuterRef("pk"))

        breakdown_query = UnConStimulusCategory.objects.values("name").distinct("name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_modality(self):
        experiments_subquery_by_breakdown = self.experiments.filter(target_stimuli__modality=OuterRef("pk"))

        breakdown_query = UnConModalityType.objects.values("name").distinct("name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_phase(self):
        experiments_subquery_by_breakdown = self.experiments.filter(unconsciousness_measures__phase=OuterRef("pk"))

        breakdown_query = (
            UnConsciousnessMeasurePhase.objects.values("name").distinct("name").annotate(series_name=F("name"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = self.experiments.filter(unconsciousness_measures__type=OuterRef("pk"))

        breakdown_query = (
            UnConsciousnessMeasureType.objects.values("name").distinct("name").annotate(series_name=F("name"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, queryset: QuerySet, filtered_subquery: QuerySet):
        # Hopefully this is generic enough to be reused
        if self.is_csv:
            ids = queryset.annotate(experiments=ArraySubquery(filtered_subquery.values_list("id"))).values_list(
                "experiments", flat=True
            )
            return set(list(itertools.chain.from_iterable(ids)))
        subquery = (
            filtered_subquery.annotate(year=F("study__year"))
            .values("year")
            .order_by("year")
            .annotate(experiment_count=Count("id", distinct=True))
            .annotate(data=JSONObject(year=F("year"), value=F("experiment_count")))
            .values_list("data")
        )

        qs = (
            queryset.values("series_name")
            .annotate(series=ArraySubquery(subquery))
            .annotate(field_len=Func(F("series"), function="CARDINALITY"))
            .filter(field_len__gt=0)
            .values("series_name", "series")
            .order_by("series_name")
        )
        # Note we're filtering out empty timeseries with the cardinality option
        retval = []
        earliest_year = None
        for series_data in list(qs):
            series = self.accumulate_inner_series_values_and_filter(
                series_data["series"], self.min_number_of_experiments
            )
            if len(series):
                earliest_year_in_series = series_data["series"][0]["year"]
                if earliest_year is None or earliest_year_in_series < earliest_year:
                    earliest_year = earliest_year_in_series
                retval.append(dict(series_name=series_data["series_name"], series=series))
        if earliest_year is not None:
            for line in retval:
                if line["series"][0]["year"] > earliest_year:
                    # todo check if I can really insert like that
                    line["series"].insert(0, dict(year=earliest_year, value=0))
        return retval