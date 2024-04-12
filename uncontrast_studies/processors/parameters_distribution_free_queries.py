import itertools

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import Func, F, Count, QuerySet, OuterRef


from uncontrast_studies.processors.base import BaseProcessor
from uncontrast_studies.models import (
    UnConSample,
    UnConExperiment,
    UnConTaskType,
    UnConStimulusCategory,
    UnConModalityType,
    UnConsciousnessMeasurePhase,
    UnConsciousnessMeasureType,
    UnConProcessingMainDomain,
    UnConMainParadigm,
)


class ParametersDistributionFreeQueriesDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)

        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]

        self.paradigms = kwargs.pop("paradigms", [])
        self.suppressed_stimuli_categories = kwargs.pop("suppressed_stimuli_categories", [])
        self.suppressed_stimuli_modalities = kwargs.pop("suppressed_stimuli_modalities", [])
        self.target_stimuli_categories = kwargs.pop("target_stimuli_categories", [])
        self.target_stimuli_modalities = kwargs.pop("target_stimuli_modalities", [])
        self.populations = kwargs.pop("populations", [])
        self.consciousness_measure_phases = kwargs.pop("consciousness_measure_phases", [])
        self.consciousness_measure_types = kwargs.pop("consciousness_measure_types", [])
        self.processing_domain_main_types = kwargs.pop("processing_domain_types", [])
        self.suppression_methods_types = kwargs.pop("suppression_methods_types", [])
        self.types = kwargs.pop("types", [])
        self.tasks = kwargs.pop("tasks", [])

    def process(self):
        """
        do a transpose "experiment per country in study" with unnest on the array field
        aggregate on country and theory relation


        """
        # First we'll filter the available experiments
        self.filtered_experiments = self.get_queryset()

        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def get_queryset(self):
        queryset = self.experiments

        # we need to support that but there is mess with modeling paradigms now
        # if len(self.paradigms):
        #     queryset = queryset.filter(paradigms__id__in=self.paradigms)
        #
        #

        if len(self.suppressed_stimuli_categories):
            queryset = queryset.filter(stimuli__category__id__in=self.suppressed_stimuli_categories)

        if len(self.suppressed_stimuli_modalities):
            queryset = queryset.filter(stimuli__modality__id__in=self.suppressed_stimuli_modalities)

        if len(self.target_stimuli_categories):
            queryset = queryset.filter(stimuli__category__id__in=self.target_stimuli_categories)

        if len(self.target_stimuli_modalities):
            queryset = queryset.filter(stimuli__modality__id__in=self.target_stimuli_modalities)

        if len(self.populations):
            queryset = queryset.filter(samples__type__in=self.populations)

        if len(self.consciousness_measure_phases):
            queryset = queryset.filter(consciousness_measures__phase__id__in=self.consciousness_measure_phases)

        if len(self.consciousness_measure_types):
            queryset = queryset.filter(consciousness_measures__type__id__in=self.consciousness_measure_types)

        if len(self.processing_domain_main_types):
            queryset = queryset.filter(processing_domains__main__id__in=self.processing_domain_main_types)

        if len(self.types):
            queryset = queryset.filter(type__in=self.types)

        if len(self.tasks):
            queryset = queryset.filter(tasks__type__id__in=self.tasks)

        if len(self.suppression_methods_types):
            queryset = queryset.filter(suppression_methods__type__id__in=self.suppression_methods_types)

        return queryset

    def process_paradigm(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            paradigms=OuterRef("pk")
        ).values("id")  # TODO: adapt this one according to the final modeling

        breakdown_query = UnConMainParadigm.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_population(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            samples__type=OuterRef("series_name")
        ).values("id")

        breakdown_query = UnConSample.objects.values("type").distinct().annotate(series_name=F("type"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_target_same_as_suppressed_stimulus(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            is_target_same_as_suppressed_stimulus=OuterRef("series_name")
        ).values("id")

        breakdown_query = (
            UnConExperiment.objects.values("is_target_same_as_suppressed_stimulus")
            .distinct()
            .annotate(series_name=F("is_target_same_as_suppressed_stimulus"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_task(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(tasks__type=OuterRef("pk")).values("id")

        breakdown_query = UnConTaskType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_category(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppressed_stimuli__category=OuterRef("pk")
        ).values("id")

        breakdown_query = UnConStimulusCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_category(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            target_stimuli__category=OuterRef("pk")
        ).values("id")

        breakdown_query = UnConStimulusCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_modality(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppressed__stimuli__modality=OuterRef("pk")
        ).values("id")

        breakdown_query = UnConModalityType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_modality(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppressed__stimuli__modality=OuterRef("pk")
        ).values("id")

        breakdown_query = UnConModalityType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_phase(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            consciousness_measures__phase=OuterRef("pk")
        ).values("id")

        breakdown_query = UnConsciousnessMeasurePhase.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            consciousness_measures__type=OuterRef("pk")
        ).values("id")

        breakdown_query = UnConsciousnessMeasureType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppression_method(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppression_methods__type=OuterRef("pk")
        ).values("experiment")

        breakdown_query = UnConProcessingMainDomain.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_processing_domain(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            experiment__processing_domains__main=OuterRef("pk")
        ).values("experiment")

        breakdown_query = UnConProcessingMainDomain.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, queryset: QuerySet, filtered_subquery: QuerySet):
        # Hopefully this is generic enough to be reused

        if self.is_csv:
            ids = queryset.annotate(experiments=ArraySubquery(filtered_subquery.values_list("id"))).values_list(
                "experiments", flat=True
            )
            return set(list(itertools.chain.from_iterable(ids)))

        annotated_subquery = filtered_subquery.annotate(experiment_count=Count("id", distinct=True))

        # todo check if need to change
        ids_subquery = annotated_subquery.order_by("experiment").values_list("experiment")

        qs = (
            queryset.values("series_name")
            .annotate(ids_list=ArraySubquery(ids_subquery))
            .annotate(value=Func(F("ids_list"), function="CARDINALITY"))
            .filter(value__gt=self.min_number_of_experiments)
            .annotate(key=F("series_name"))
            .values("key", "value")
            .order_by("-value", "key")
        )
        return qs
