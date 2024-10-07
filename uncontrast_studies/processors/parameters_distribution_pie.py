import itertools

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Func, Count
from django.db.models.functions import JSONObject


from uncontrast_studies.models import (
    UnConExperiment,
    UnConSample,
    UnConModalityType,
    UnConStimulusCategory,
    UnConsciousnessMeasureType,
    UnConsciousnessMeasurePhase,
    UnConTaskType,
    UnConOutcome,
    UnConProcessingMainDomain,
    UnConSuppressedStimulus,
    UnConSuppressionMethodType,
    UnConMainParadigm,
    UnConsciousnessMeasure,
    UnConTargetStimulus,
    UnConStimulusSubCategory,
)
from uncontrast_studies.processors.base import BaseProcessor


class ParametersDistributionPieGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]

    def process(self):
        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def process_paradigm(self):
        experiments_subquery_by_breakdown = self.experiments.filter(paradigm__main=OuterRef("pk"))

        breakdown_query = UnConMainParadigm.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_population(self):
        experiments_subquery_by_breakdown = self.experiments.filter(samples__type=OuterRef("type"))

        breakdown_query = UnConSample.objects.values("type").order_by("type").distinct().annotate(series_name=F("type"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_performance_above_chance(self):
        experiments_subquery_by_breakdown = self.experiments.filter(
            unconsciousness_measures__is_performance_above_chance=OuterRef("series_name")
        ).values("id", "significance")

        breakdown_query = (
            UnConsciousnessMeasure.objects.values("is_performance_above_chance")
            .distinct()
            .annotate(series_name=F("is_performance_above_chance"))
        )
        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_target_same_as_suppressed_stimulus(self):
        experiments_subquery_by_breakdown = self.experiments.filter(
            target_stimuli__is_target_same_as_suppressed_stimulus=OuterRef("series_name")
        )

        breakdown_query = (
            UnConTargetStimulus.objects.values("is_target_same_as_suppressed_stimulus")
            .distinct()
            .annotate(series_name=F("is_target_same_as_suppressed_stimulus"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppression_method(self):
        experiments_subquery_by_breakdown = self.experiments.filter(
            suppression_methods__type__name=OuterRef("series_name")
        )

        breakdown_query = UnConSuppressionMethodType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_processing_domain(self):
        experiments_subquery_by_breakdown = self.experiments.filter(
            processing_domains__main__name=OuterRef("series_name")
        )

        breakdown_query = UnConProcessingMainDomain.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_task(self):
        experiments_subquery_by_breakdown = self.experiments.filter(tasks__type=OuterRef("pk"))

        breakdown_query = UnConTaskType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_outcome_type(self):
        experiments_subquery_by_breakdown = self.experiments.filter(findings__outcome=OuterRef("pk"))

        breakdown_query = UnConOutcome.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_category(self):
        experiments_subquery_by_breakdown = self.experiments.filter(suppressed_stimuli__category=OuterRef("pk"))

        breakdown_query = UnConStimulusCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_sub_category(self):
        experiments_subquery_by_breakdown = self.experiments.filter(suppressed_stimuli__sub_category=OuterRef("pk"))

        breakdown_query = (
            UnConStimulusSubCategory.objects.values("name").distinct("name").annotate(series_name=F("name"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_sub_category(self):
        experiments_subquery_by_breakdown = self.experiments.filter(target_stimuli__sub_category=OuterRef("pk"))

        breakdown_query = (
            UnConStimulusSubCategory.objects.values("name").distinct("name").annotate(series_name=F("name"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_category(self):
        experiments_subquery_by_breakdown = self.experiments.filter(target_stimuli__category=OuterRef("pk"))

        breakdown_query = UnConStimulusCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_modality(self):
        experiments_subquery_by_breakdown = self.experiments.filter(suppressed_stimuli__modality=OuterRef("pk"))

        breakdown_query = UnConModalityType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_modality(self):
        experiments_subquery_by_breakdown = self.experiments.filter(target_stimuli__modality=OuterRef("pk"))

        breakdown_query = UnConModalityType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_phase(self):
        experiments_subquery_by_breakdown = self.experiments.filter(unconsciousness_measures__phase=OuterRef("pk"))

        breakdown_query = UnConsciousnessMeasurePhase.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_cm_same_participants_as_task(self):
        experiments_subquery_by_breakdown = self.experiments.filter(
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
        experiments_subquery_by_breakdown = self.experiments.filter(
            unconsciousness_measures__is_trial_excluded_based_on_measure=OuterRef("series_name")
        ).values("id")

        breakdown_query = (
            UnConsciousnessMeasure.objects.values("is_trial_excluded_based_on_measure")
            .distinct()
            .annotate(series_name=F("is_trial_excluded_based_on_measure"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_modes_of_presentation(self):
        experiments_subquery_by_breakdown = self.experiments.filter(
            suppressed_stimuli__mode_of_presentation=OuterRef("series_name")
        )
        breakdown_query = (
            UnConSuppressedStimulus.objects.values("mode_of_presentation")
            .distinct()
            .annotate(series_name=F("mode_of_presentation"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = self.experiments.filter(unconsciousness_measures__type=OuterRef("pk"))

        breakdown_query = UnConsciousnessMeasureType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, queryset: QuerySet, filtered_subquery: QuerySet):
        option_subquery = filtered_subquery.values("significance").annotate(experiment_count=Count("id", distinct=True))

        if self.is_csv:
            ids = queryset.annotate(experiments=ArraySubquery(filtered_subquery.values_list("id"))).values_list(
                "experiments", flat=True
            )
            return set(list(itertools.chain.from_iterable(ids)))

        subquery = (
            option_subquery.order_by("-experiment_count")
            .filter(experiment_count__gt=self.min_number_of_experiments)
            .annotate(data=JSONObject(key=F("significance"), value=F("experiment_count")))
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
        for dataset in list(qs):
            dataset["value"] = self.accumulate_total_from_series(dataset["series"])
            retval.append(dataset)
        return sorted(retval, key=lambda x: x["value"], reverse=True)
