from django.db.models import QuerySet, F, Count
from django.db.models.functions import JSONObject

from contrast_api.choices import SignificanceChoices

from uncontrast_studies.models import (
    UnConSample,
    UnConModalityType,
    UnConStimulusCategory,
    UnConsciousnessMeasureType,
    UnConsciousnessMeasurePhase,
    UnConTaskType,
    UnConProcessingMainDomain,
    UnConSuppressedStimulus,
    UnConSuppressionMethodType, UnConTargetStimulus,
)
from uncontrast_studies.models import UnConExperiment
from uncontrast_studies.processors.base import BaseProcessor


class ComparisonParametersDistributionPieGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]

    def process(self):
        return self.aggregate_query_by_breakdown()

    def get_query(self, experiments: QuerySet[UnConExperiment]):
        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func(experiments)

    def process_paradigm(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            experiments.distinct()
            .values("paradigm")
            .annotate(experiment_count=Count("id", distinct=True))
            .annotate(key=F("paradigm"))
        )
        return subquery

    def process_population(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            UnConSample.objects.filter(experiment__in=experiments)
            .distinct()
            .values("type")
            .annotate(experiment_count=Count("experiment", distinct=True))
            .annotate(key=F("type"))
        )

        return subquery

    def process_task(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            UnConTaskType.objects.filter(tasks__experiment__in=experiments)
            .distinct()
            .values("name")
            .annotate(experiment_count=Count("tasks__experiment", distinct=True))
            .annotate(key=F("name"))
        )

        return subquery

    def process_suppressed_stimuli_category(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            UnConStimulusCategory.objects.filter(suppressed_stimuli__experiment__in=experiments)
            .distinct()
            .values("name")
            .annotate(experiment_count=Count("suppressed_stimuli__experiment", distinct=True))
            .annotate(key=F("name"))
        )

        return subquery

    def process_target_stimuli_category(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            UnConStimulusCategory.objects.filter(target_stimuli__experiment__in=experiments)
            .distinct()
            .values("name")
            .annotate(experiment_count=Count("target_stimuli__experiment", distinct=True))
            .annotate(key=F("name"))
        )

        return subquery

    def process_suppressed_stimuli_modality(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            UnConModalityType.objects.filter(suppressed_stimuli__experiment__in=experiments)
            .distinct()
            .values("name")
            .annotate(experiment_count=Count("suppressed_stimuli__experiment", distinct=True))
            .annotate(key=F("name"))
        )

        return subquery

    def process_target_stimuli_modality(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            UnConModalityType.objects.filter(target_stimuli__experiment__in=experiments)
            .distinct()
            .values("name")
            .annotate(experiment_count=Count("target_stimuli__experiment", distinct=True))
            .annotate(key=F("name"))
        )

        return subquery

    def process_consciousness_measure_phase(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            UnConsciousnessMeasurePhase.objects.filter(unconsciousness_measures__experiment__in=experiments)
            .distinct()
            .values("name")
            .annotate(experiment_count=Count("unconsciousness_measures__experiment", distinct=True))
            .annotate(key=F("name"))
        )

        return subquery

    def process_consciousness_measure_type(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            UnConsciousnessMeasureType.objects.filter(unconsciousness_measures__experiment__in=experiments)
            .distinct()
            .values("name")
            .annotate(experiment_count=Count("unconsciousness_measures__experiment", distinct=True))
            .annotate(key=F("name"))
        )

        return subquery

    def process_processing_domain(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            UnConProcessingMainDomain.objects.filter(processing_domains__experiment__in=experiments)
            .distinct()
            .values("name")
            .annotate(experiment_count=Count("processing_domains__experiment", distinct=True))
            .annotate(key=F("name"))
        )

        return subquery

    def process_suppression_method(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            UnConSuppressionMethodType.objects.filter(suppression_methods__experiment__in=experiments)
            .distinct()
            .values("name")
            .annotate(experiment_count=Count("suppression_methods__experiment", distinct=True))
            .annotate(key=F("name"))
        )

        return subquery

    def process_is_target_same_as_suppressed_stimulus(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            experiments.distinct()
            .values("target_stimuli__is_target_same_as_suppressed_stimulus")
            .annotate(experiment_count=Count("id", distinct=True))
            .annotate(key=F("target_stimuli__is_target_same_as_suppressed_stimulus"))
        )

        return subquery

    def process_is_performance_above_chance(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            experiments.distinct()
            .values("unconsciousness_measures__is_performance_above_chance")
            .annotate(experiment_count=Count("id", distinct=True))
            .annotate(key=F("unconsciousness_measures__is_performance_above_chance"))
        )

        return subquery

    def process_is_cm_same_participants_as_task(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            experiments.distinct()
            .values("unconsciousness_measures__is_cm_same_participants_as_task")
            .annotate(experiment_count=Count("id", distinct=True))
            .annotate(key=F("unconsciousness_measures__is_cm_same_participants_as_task"))
        )

        return subquery

    def process_is_trial_excluded_based_on_measure(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            experiments.distinct()
            .values("unconsciousness_measures__is_trial_excluded_based_on_measure")
            .annotate(experiment_count=Count("id", distinct=True))
            .annotate(key=F("unconsciousness_measures__is_trial_excluded_based_on_measure"))
        )

        return subquery

    def process_modes_of_presentation(self, experiments: QuerySet[UnConExperiment]):
        subquery = (
            UnConSuppressedStimulus.objects.filter(experiment__in=experiments)
            .distinct()
            .values("mode_of_presentation")
            .annotate(experiment_count=Count("experiment", distinct=True))
            .annotate(key=F("mode_of_presentation"))
        )

        return subquery

    def aggregate_query_by_breakdown(self):
        significance_options = SignificanceChoices.values

        results = []
        experiment_ids = []
        for sig_option in significance_options:
            experiments_for_option = (
                self.experiments.filter(significance=sig_option).distinct().values_list("id", flat=True)
            )
            if self.is_csv:
                option_experiment_ids = experiments_for_option.values_list("id", flat=True)

                experiment_ids += option_experiment_ids
            else:
                subquery = self.get_query(experiments_for_option)

                subquery_by_breakdown = (
                    subquery.order_by("-experiment_count")
                    .filter(experiment_count__gt=self.min_number_of_experiments)
                    .annotate(data=JSONObject(key=F("key"), value=F("experiment_count")))
                    .values_list("data", flat=True)
                )

                if len(subquery_by_breakdown) > 0:
                    series = list(subquery_by_breakdown)
                    total_value = self.accumulate_total_from_series(series)
                    result = dict(series=series, series_name=sig_option, value=total_value)
                    results.append(result)
        if self.is_csv:
            return set(experiment_ids)

        return results
