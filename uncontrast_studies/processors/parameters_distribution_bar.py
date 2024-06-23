import itertools

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Func, Count
from django.db.models.functions import JSONObject

from uncontrast_studies.processors.base import BaseProcessor
from uncontrast_studies.models import (
    UnConMainParadigm,
    UnConExperiment,
    UnConSample,
    UnConTaskType,
    UnConModalityType,
    UnConStimulusCategory,
    UnConProcessingMainDomain,
    UnConsciousnessMeasureType,
    UnConsciousnessMeasurePhase,
    UnConSuppressedStimulus,
    UnConsciousnessMeasure,
    UnConTargetStimulus,
    UnConStimulusSubCategory,
    UnConSuppressionMethodType,
)


class ParametersDistributionBarGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]
        # Just so i can copy paste the methods
        self.filtered_experiments = self.experiments

    def process(self):
        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def process_paradigm(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(paradigm__main=OuterRef("pk")).values(
            "id", "significance"
        )

        breakdown_query = UnConMainParadigm.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_population(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            samples__type=OuterRef("series_name")
        ).values("id", "significance")

        breakdown_query = UnConSample.objects.values("type").distinct().annotate(series_name=F("type"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_target_same_as_suppressed_stimulus(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            target_stimuli__is_target_same_as_suppressed_stimulus=OuterRef("series_name")
        ).values("id", "significance")

        breakdown_query = (
            UnConTargetStimulus.objects.values("is_target_same_as_suppressed_stimulus")
            .distinct()
            .annotate(series_name=F("is_target_same_as_suppressed_stimulus"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_task(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(tasks__type=OuterRef("pk")).values(
            "id", "significance"
        )

        breakdown_query = UnConTaskType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_category(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppressed_stimuli__category=OuterRef("pk")
        ).values("id", "significance")

        breakdown_query = UnConStimulusCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_sub_category(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppressed_stimuli__sub_category=OuterRef("pk")
        ).values("id", "significance")

        breakdown_query = UnConStimulusSubCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_sub_category(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            target_stimuli__sub_category=OuterRef("pk")
        ).values("id", "significance")

        breakdown_query = UnConStimulusSubCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_category(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            target_stimuli__category=OuterRef("pk")
        ).values("id", "significance")

        breakdown_query = UnConStimulusCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_modality(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppressed_stimuli__modality=OuterRef("pk")
        ).values("id", "significance")

        breakdown_query = UnConModalityType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_modality(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppressed_stimuli__modality=OuterRef("pk")
        ).values("id", "significance")

        breakdown_query = UnConModalityType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_performance_above_chance(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            unconsciousness_measures__is_performance_above_chance=OuterRef("series_name")
        ).values("id", "significance")

        breakdown_query = (
            UnConsciousnessMeasure.objects.values("is_performance_above_chance")
            .distinct()
            .annotate(series_name=F("is_performance_above_chance"))
        )
        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_cm_same_participants_as_task(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            unconsciousness_measures__is_cm_same_participants_as_task=OuterRef("series_name")
        ).values("id", "significance")

        breakdown_query = (
            UnConsciousnessMeasure.objects.values("is_cm_same_participants_as_task")
            .distinct()
            .annotate(series_name=F("is_cm_same_participants_as_task"))
        )
        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_trial_excluded_based_on_measure(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            unconsciousness_measures__is_trial_excluded_based_on_measure=OuterRef("series_name")
        ).values("id")

        breakdown_query = (
            UnConsciousnessMeasure.objects.values("is_trial_excluded_based_on_measure")
            .distinct()
            .annotate(series_name=F("is_trial_excluded_based_on_measure"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_phase(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            unconsciousness_measures__phase=OuterRef("pk")
        ).values("id", "significance")

        breakdown_query = UnConsciousnessMeasurePhase.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            unconsciousness_measures__type=OuterRef("pk")
        ).values("id", "significance")

        breakdown_query = UnConsciousnessMeasureType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppression_method(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppression_methods__type=OuterRef("pk")
        ).values("id", "significance")

        breakdown_query = UnConSuppressionMethodType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_processing_domain(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            processing_domains__main=OuterRef("pk")
        ).values("id", "significance")

        breakdown_query = UnConProcessingMainDomain.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_modes_of_presentation(self):
        experiments_subquery_by_breakdown = (
            self.filtered_experiments.filter(suppressed_stimuli__mode_of_presentation=OuterRef("series_name"))
        ).values("id", "significance")

        breakdown_query = (
            UnConSuppressedStimulus.objects.values("mode_of_presentation")
            .distinct()
            .annotate(series_name=F("mode_of_presentation"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, queryset: QuerySet, filtered_subquery: QuerySet):
        # Hopefully this is generic enough to be reused
        by_significance = (
            filtered_subquery.values("significance")
            .order_by("-significance")
            .annotate(experiment_count=Count("id", distinct=True))
        )
        subquery = by_significance.annotate(
            data=JSONObject(key=F("significance"), value=F("experiment_count"))
        ).values_list("data")

        ids_subquery = by_significance.order_by("id").values_list("id")

        if self.is_csv:
            ids = queryset.annotate(experiments=ArraySubquery(filtered_subquery.values_list("id"))).values_list(
                "experiments", flat=True
            )
            return set(list(itertools.chain.from_iterable(ids)))

        qs = (
            queryset.values("series_name")
            .annotate(series=ArraySubquery(subquery))
            .annotate(ids_list=ArraySubquery(ids_subquery))
            .annotate(totals=Func(F("ids_list"), function="CARDINALITY"))
            .annotate(field_len=Func(F("series"), function="CARDINALITY"))
            .filter(field_len__gt=0)
            .filter(totals__gt=self.min_number_of_experiments)
            .values("series_name", "series", "totals")
            .order_by("-totals", "series_name")
        )
        # Note we're filtering out empty timeseries with the cardinality option
        # TODO order by total of inner values
        return qs
