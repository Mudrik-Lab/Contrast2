import itertools

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import Func, F, Count, QuerySet, OuterRef, Case, When, Value, Q, CharField, Exists

from contrast_api.utils import cast_as_boolean
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
    UnConsciousnessMeasure,
    UnConSuppressedStimulus,
    UnConTargetStimulus,
    UnConStimulusSubCategory,
    UnConSuppressionMethodType,
    UnConOutcome,
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
        self.modes_of_presentation = kwargs.pop("modes_of_presentation", [])
        self.outcome_types = kwargs.pop("outcome_types", [])
        self.is_trial_excluded_based_on_measure = kwargs.pop("is_trial_excluded_based_on_measure", [])
        are_participants_excluded = kwargs.pop("are_participants_excluded", [])
        self.are_participants_excluded = [cast_as_boolean(x) for x in are_participants_excluded]

        self.types = kwargs.pop("types", [])
        self.tasks = kwargs.pop("tasks", [])

    def process(self):
        """ """
        # First we'll filter the available experiments
        self.filtered_experiments = self.get_queryset()

        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def get_queryset(self):
        queryset = self.experiments

        # we need to support that but there is mess with modeling paradigms now
        if len(self.paradigms):
            queryset = queryset.filter(paradigm__main__id__in=self.paradigms)

        if len(self.suppressed_stimuli_categories):
            queryset = queryset.filter(suppressed_stimuli__category__id__in=self.suppressed_stimuli_categories)

        if len(self.suppressed_stimuli_modalities):
            queryset = queryset.filter(suppressed_stimuli__modality__id__in=self.suppressed_stimuli_modalities)

        if len(self.modes_of_presentation):
            queryset = queryset.filter(suppressed_stimuli__mode_of_presentation__in=self.modes_of_presentation)

        if len(self.target_stimuli_categories):
            queryset = queryset.filter(target_stimuli__category__id__in=self.target_stimuli_categories)

        if len(self.target_stimuli_modalities):
            queryset = queryset.filter(target_stimuli__modality__id__in=self.target_stimuli_modalities)

        if len(self.populations):
            queryset = queryset.filter(samples__type__in=self.populations)

        if len(self.consciousness_measure_phases):
            queryset = queryset.filter(unconsciousness_measures__phase__id__in=self.consciousness_measure_phases)

        if len(self.consciousness_measure_types):
            queryset = queryset.filter(unconsciousness_measures__type__id__in=self.consciousness_measure_types)

        if len(self.processing_domain_main_types):
            queryset = queryset.filter(processing_domains__main__id__in=self.processing_domain_main_types)

        if len(self.types):
            queryset = queryset.filter(type__in=self.types)

        if len(self.tasks):
            queryset = queryset.filter(tasks__type__id__in=self.tasks)

        if len(self.suppression_methods_types):
            queryset = queryset.filter(suppression_methods__type__id__in=self.suppression_methods_types)

        if len(self.outcome_types):
            # TODO: fix this later to use the type
            queryset = queryset.filter(findings__outcome__in=self.outcome_types)

        if len(self.is_trial_excluded_based_on_measure):
            queryset = queryset.filter(
                unconsciousness_measures__is_trial_excluded_based_on_measure__in=self.is_trial_excluded_based_on_measure
            )

        if len(self.are_participants_excluded):
            queryset = queryset.annotate(
                are_participants_excluded=Case(
                    When(samples__size_excluded__gt=0, then=Value(True)), default=Value(False)
                )
            ).filter(are_participants_excluded__in=self.are_participants_excluded)
        return queryset

    def process_paradigm(self):
        """
        Note this is main paradigm
        """
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(paradigm__main=OuterRef("pk")).values("id")

        breakdown_query = UnConMainParadigm.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_population(self):
        """
        This is about samples, keeping the historic name for parity with contrast
        """
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            samples__type=OuterRef("series_name")
        ).values("id")

        breakdown_query = UnConSample.objects.values("type").distinct().annotate(series_name=F("type"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_modes_of_presentation(self):
        """ """
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppressed_stimuli__mode_of_presentation=OuterRef("series_name")
        ).values("id")

        breakdown_query = (
            UnConSuppressedStimulus.objects.values("mode_of_presentation")
            .distinct()
            .annotate(series_name=F("mode_of_presentation"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_target_same_as_suppressed_stimulus(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            target_stimuli__is_target_same_as_suppressed_stimulus=OuterRef("series_name")
        ).values("id")

        breakdown_query = (
            UnConTargetStimulus.objects.values("is_target_same_as_suppressed_stimulus")
            .distinct()
            .annotate(series_name=F("is_target_same_as_suppressed_stimulus"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_cm_same_participants_as_task(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            unconsciousness_measures__is_cm_same_participants_as_task=OuterRef("series_name")
        ).values("id")

        breakdown_query = (
            UnConsciousnessMeasure.objects.values("is_cm_same_participants_as_task")
            .distinct()
            .annotate(series_name=F("is_cm_same_participants_as_task"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_is_performance_above_chance(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            unconsciousness_measures__is_performance_above_chance=OuterRef("series_name")
        ).values("id")

        breakdown_query = (
            UnConsciousnessMeasure.objects.values("is_performance_above_chance")
            .distinct()
            .annotate(series_name=F("is_performance_above_chance"))
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

    def process_task(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(tasks__type=OuterRef("pk")).values("id")

        breakdown_query = UnConTaskType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_outcome_type(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(findings__outcome=OuterRef("pk")).values(
            "id"
        )

        breakdown_query = UnConOutcome.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_category(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppressed_stimuli__category=OuterRef("pk")
        ).values("id")

        breakdown_query = UnConStimulusCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppressed_stimuli_sub_category(self):
        experiments_subquery_by_breakdown = self.experiments.filter(suppressed_stimuli__sub_category=OuterRef("pk"))

        breakdown_query = UnConStimulusSubCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_sub_category(self):
        experiments_subquery_by_breakdown = self.experiments.filter(target_stimuli__sub_category=OuterRef("pk"))

        breakdown_query = UnConStimulusSubCategory.objects.values("name").distinct().annotate(series_name=F("name"))

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
            suppressed_stimuli__modality=OuterRef("pk")
        ).values("id")

        breakdown_query = UnConModalityType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_target_stimuli_modality(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            target_stimuli__modality=OuterRef("pk")
        ).values("id")

        breakdown_query = UnConModalityType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_phase(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            unconsciousness_measures__phase=OuterRef("pk")
        ).values("id")

        breakdown_query = UnConsciousnessMeasurePhase.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = (
            self.filtered_experiments.annotate(
                measure_type=Case(
                    When(
                        Exists(UnConsciousnessMeasure.objects.filter(experiment=OuterRef("pk"), type__name="Objective"))
                        & Exists(
                            UnConsciousnessMeasure.objects.filter(experiment=OuterRef("pk"), type__name="Subjective")
                        ),
                        then=Value("Both"),
                    ),
                    default=Value(None),
                    output_field=CharField(null=True),
                )
            )
            .filter(
                Q(measure_type=OuterRef("name"))
                |
                # we need to remove the case where the type is Objective/Subjective
                (Q(unconsciousness_measures__type__name=OuterRef("name")) & Q(measure_type__isnull=True))
            )
            .values("id")
        )

        breakdown_query = UnConsciousnessMeasureType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_suppression_method(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            suppression_methods__type=OuterRef("pk")
        ).values("id")

        breakdown_query = UnConSuppressionMethodType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_processing_domain(self):
        experiments_subquery_by_breakdown = self.filtered_experiments.filter(
            processing_domains__main=OuterRef("pk")
        ).values("id")

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
        ids_subquery = annotated_subquery.order_by("id").values_list("id")

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
