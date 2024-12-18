import itertools

from django.db.models import QuerySet, F, Count, Value, When, Case, Q, Exists, OuterRef
from django.db.models.fields import CharField

from contrast_api.utils import cast_as_boolean
from uncontrast_studies.models import UnConExperiment, UnConsciousnessMeasureType, UnConsciousnessMeasure
from uncontrast_studies.processors.base import BaseProcessor


class GrandOverviewPieGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
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
        self.filtered_experiments = self.get_queryset()

        process_func = getattr(self, "process_significance")
        return process_func()

    def process_significance(self):
        experiments_subquery_by_breakdown = self.filtered_experiments

        qs = self._aggregate_query_by_breakdown(experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, experiments: QuerySet[UnConExperiment]):
        if self.is_csv:
            ids = experiments.values_list("id", flat=True)
            return set(list(itertools.chain.from_iterable(ids)))

        """
        Discussion: Unlike most, we don't have "two" levels of grouping here 
        (e.g the series_name is the subset by paradigm, or whatever we're measuring 
        and the actual series data for each subset)
        I wanted to keep the general structure of the code the same, so I'm not using
        "aggregate" which might have been better here, but returning an array with annotate with as single item
        
        """
        total_value = experiments.aggregate(total_value=Count("id", distinct=True))["total_value"]

        aggregated_qs = (
            experiments.annotate(key=F("significance"))
            .values("key")
            .annotate(value=Count("id", distinct=True))
            .filter(value__gt=self.min_number_of_experiments)
            .order_by("-value")
        )
        result = {"series_name": "Grand Overview", "series": list(aggregated_qs), "value": total_value}
        return result

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
            both = UnConsciousnessMeasureType.objects.get(name="Both")

            if str(both.id) in self.consciousness_measure_types:
                queryset = queryset.annotate(
                    measure_type=Case(
                        When(
                            Exists(
                                UnConsciousnessMeasure.objects.filter(experiment=OuterRef("id"), type__name="Objective")
                            )
                            & Exists(
                                UnConsciousnessMeasure.objects.filter(
                                    experiment=OuterRef("id"), type__name="Subjective"
                                )
                            ),
                            then=Value("Both"),
                        ),
                        default=Value(None),
                        output_field=CharField(null=True),
                    )
                ).filter(
                    Q(measure_type="Both") | Q(unconsciousness_measures__type__id__in=self.consciousness_measure_types)
                )
                queryset
            else:
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
