from django.db.models import QuerySet, F, Count
from django.db.models.functions import JSONObject

from studies.models import Experiment, Paradigm, Interpretation, Sample, FindingTagType, FindingTagFamily, TaskType, \
    ModalityType, ConsciousnessMeasurePhaseType, ConsciousnessMeasureType, Technique, MeasureType, Theory
from studies.models.stimulus import StimulusCategory
from studies.processors.base import BaseProcessor


class ComparisonParametersDistributionPieGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]
        interpretation = kwargs.pop("interpretation")
        self.interpretation = interpretation[0]

    def process(self):
        return self.aggregate_query_by_breakdown()

    def get_query(self, theory_interpretations_experiments):
        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func(theory_interpretations_experiments)

    def process_paradigm_family(self, theory_interpretations_experiments):
        # Children_experiments is referring from theory to child theory and from their to "experiments"
        subquery = Paradigm.objects.filter(parent__isnull=True) \
            .filter(child_paradigm__experiments__in=theory_interpretations_experiments) \
            .distinct() \
            .values("name") \
            .annotate(experiment_count=Count("child_paradigm__experiments", distinct=True)) \
            .annotate(key=F("name"))

        return subquery

    def process_paradigm(self, theory_interpretations_experiments):
        subquery = Paradigm.objects.filter(parent__isnull=False) \
            .filter(experiments__in=theory_interpretations_experiments) \
            .distinct() \
            .values("name") \
            .annotate(experiment_count=Count("experiments", distinct=True)) \
            .annotate(key=F("name"))

        return subquery

    def process_population(self, theory_interpretations_experiments):
        subquery = Sample.objects \
            .filter(experiment__in=theory_interpretations_experiments) \
            .distinct() \
            .values("type") \
            .annotate(experiment_count=Count("experiment", distinct=True)) \
            .annotate(key=F("type"))

        return subquery

    def process_finding_tag(self, theory_interpretations_experiments):
        subquery = FindingTagType.objects \
            .filter(findingtag__experiment__in=theory_interpretations_experiments) \
            .distinct() \
            .values("name") \
            .annotate(experiment_count=Count("findingtag__experiment", distinct=True)) \
            .annotate(key=F("name"))

        return subquery

    def process_finding_tag_family(self, theory_interpretations_experiments):
        subquery = FindingTagFamily.objects \
            .filter(findingtag__experiment__in=theory_interpretations_experiments) \
            .distinct() \
            .values("name") \
            .annotate(experiment_count=Count("findingtag__experiment", distinct=True)) \
            .annotate(key=F("name"))

        return subquery

    def process_reporting(self, theory_interpretations_experiments):
        subquery = Experiment.objects \
            .filter(id__in=theory_interpretations_experiments) \
            .distinct() \
            .values("is_reporting") \
            .annotate(experiment_count=Count("id", distinct=True)) \
            .annotate(key=F("is_reporting"))

        return subquery

    def process_theory_driven(self, theory_interpretations_experiments):
        subquery = Experiment.objects \
            .filter(id__in=theory_interpretations_experiments) \
            .distinct() \
            .values("theory_driven") \
            .annotate(experiment_count=Count("id", distinct=True)) \
            .annotate(key=F("theory_driven"))

        return subquery

    def process_task(self, theory_interpretations_experiments):
        subquery = TaskType.objects \
            .filter(task__experiment__in=theory_interpretations_experiments) \
            .distinct() \
            .values("name") \
            .annotate(experiment_count=Count("task__experiment", distinct=True)) \
            .annotate(key=F("name"))

        return subquery

    def process_stimuli_category(self, theory_interpretations_experiments):
        subquery = StimulusCategory.objects \
            .filter(stimuli__experiment__in=theory_interpretations_experiments) \
            .distinct() \
            .values("name") \
            .annotate(experiment_count=Count("stimuli__experiment", distinct=True)) \
            .annotate(key=F("name"))

        return subquery

    def process_modality(self, theory_interpretations_experiments):
        subquery = ModalityType.objects \
            .filter(stimuli__experiment__in=theory_interpretations_experiments) \
            .distinct() \
            .values("name") \
            .annotate(experiment_count=Count("stimuli__experiment", distinct=True)) \
            .annotate(key=F("name"))

        return subquery

    def process_consciousness_measure_phase(self, theory_interpretations_experiments):
        subquery = ConsciousnessMeasurePhaseType.objects \
            .filter(consciousness_measures__experiment__in=theory_interpretations_experiments) \
            .distinct() \
            .values("name") \
            .annotate(experiment_count=Count("consciousness_measures__experiment", distinct=True)) \
            .annotate(key=F("name"))

        return subquery

    def process_consciousness_measure_type(self, theory_interpretations_experiments):
        subquery = ConsciousnessMeasureType.objects \
            .filter(consciousness_measures__experiment__in=theory_interpretations_experiments) \
            .distinct() \
            .values("name") \
            .annotate(experiment_count=Count("consciousness_measures__experiment", distinct=True)) \
            .annotate(key=F("name"))

        return subquery

    def process_type_of_consciousness(self, theory_interpretations_experiments):
        subquery = Experiment.objects \
            .filter(id__in=theory_interpretations_experiments) \
            .distinct() \
            .values("type_of_consciousness") \
            .annotate(experiment_count=Count("id", distinct=True)) \
            .annotate(key=F("type_of_consciousness"))

        return subquery

    def process_technique(self, theory_interpretations_experiments):
        subquery = Technique.objects \
            .filter(experiments__in=theory_interpretations_experiments) \
            .distinct() \
            .values("name") \
            .annotate(experiment_count=Count("experiments", distinct=True)) \
            .annotate(key=F("name"))

        return subquery

    def process_measure(self, theory_interpretations_experiments):
        subquery = MeasureType.objects \
            .filter(measures__experiment__in=theory_interpretations_experiments) \
            .distinct() \
            .values("name") \
            .annotate(experiment_count=Count("measures__experiment", distinct=True)) \
            .annotate(key=F("name"))

        return subquery

    def aggregate_query_by_breakdown(self):
        parent_theories = Theory.objects.filter(parent__isnull=True)

        results = []
        experiment_ids = []
        for theory in parent_theories:
            theory_interpretations_experiments = Interpretation.objects.filter(type=self.interpretation,
                                                                               theory__parent=theory) \
                .filter(experiment__in=self.experiments) \
                .distinct() \
                .values_list("experiment", flat=True)
            # Children_experiments is referring from theory to child theory and from their to "experiments"
            if self.is_csv:
                theory_experiment_ids = theory_interpretations_experiments.values_list("experiment_id", flat=True)

                experiment_ids += theory_experiment_ids
            else:
                subquery = self.get_query(theory_interpretations_experiments)

                subquery_by_breakdown = subquery.order_by("-experiment_count") \
                    .filter(experiment_count__gt=self.min_number_of_experiments) \
                    .annotate(data=JSONObject(key=F("key"), value=F("experiment_count"))) \
                    .values_list("data", flat=True)

                if len(subquery_by_breakdown) > 0:
                    series = list(subquery_by_breakdown)
                    total_value = self.accumulate_total_from_series(series)
                    result = dict(
                        series=series,
                        series_name=theory.acronym,
                        value=total_value
                    )
                    results.append(result)
        if self.is_csv:
            return set(experiment_ids)

        return results
