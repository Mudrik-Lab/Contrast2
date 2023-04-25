from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Func, Subquery, Count, Sum, IntegerField, Value
from django.db.models.functions import JSONObject

from contrast_api.orm_helpers import SubqueryCount
from studies.choices import InterpretationsChoices
from studies.models import Experiment, Paradigm, Interpretation, Sample, FindingTagType, FindingTagFamily, TaskType, \
    ModalityType, ConsciousnessMeasurePhaseType, ConsciousnessMeasureType, Technique, MeasureType, Theory
from studies.models.stimulus import StimulusCategory
from studies.processors.base import BaseProcessor


def accumlate_value_from_series(series) -> int:
    total = 0
    for result in series:
        total = total + result["value"]
    return total


class ComparisonParametersDistributionPieGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]
        interpretation = kwargs.pop("interpretation")
        self.interpretation = interpretation[0]

    def process(self):
        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def process_paradigm_family(self):
        parent_theories = Theory.objects.filter(parent__isnull=True)

        results = []
        for theory in parent_theories:
            theory_interpretations_experiments = Interpretation.objects.filter(type=self.interpretation,
                                                                               theory__parent=theory) \
                .filter(experiment__in=self.experiments) \
                .distinct() \
                .values_list("experiment", flat=True)
            # Children_experiments is referring from theory to child theory and from their to "experiments"
            subquery = Paradigm.objects.filter(parent__isnull=True) \
                .filter(child_paradigm__experiments__in=theory_interpretations_experiments) \
                .distinct() \
                .values("name") \
                .annotate(experiment_count=Count("child_paradigm__experiments", distinct=True)) \
                .annotate(key=F("name"))

            subquery_by_breakdown = subquery.order_by("-experiment_count") \
                .annotate(data=JSONObject(key=F("key"), value=F("experiment_count"))) \
                .values_list("data", flat=True)

            # ids_subquery = subquery.values_list("id")

            if len(subquery_by_breakdown) > 0:
                series = list(subquery_by_breakdown)
                total_value = accumlate_value_from_series(series)
                result = dict(
                    series=series,
                    series_name=theory.name,
                    value=total_value
                )
                results.append(result)

        return results

    def _aggregate_query_by_breakdown(self, filtered_subquery: QuerySet):
        parent_theories = Theory.objects.filter(parent__isnull=True)

        subquery = filtered_subquery
        subquery = subquery \
            .order_by() \
            .annotate(data=JSONObject(key=F("key"), value=F("experiment_count"))) \
            .values_list("data")

        ids_subquery = subquery
        # .values_list("experiment_id")

        annotated_queryset = parent_theories \
            .annotate(series_name=F("name")) \
            .annotate(series=ArraySubquery(subquery)) \
            .annotate(value=Value(0)) \
            .order_by("series_name") \
            .values("series_name", "series", "value")

        qs = [annotated_queryset.filter(name=theory.name).get() for theory in parent_theories.all()]
        return qs

    def process_paradigm(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__paradigms=OuterRef("pk"))

        breakdown_query = Paradigm.objects.filter(parent__isnull=False).values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_population(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__samples=OuterRef("pk"))

        breakdown_query = Sample.objects.values("type") \
            .distinct(). \
            annotate(series_name=F("type"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__finding_tags__type=OuterRef("pk"))

        breakdown_query = FindingTagType.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag_family(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__finding_tags__family=OuterRef("pk"))

        breakdown_query = FindingTagFamily.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_reporting(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__is_reporting=OuterRef("series_name"))

        breakdown_query = Experiment.objects.values("is_reporting") \
            .distinct() \
            .annotate(series_name=F("is_reporting"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_theory_driven(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__theory_driven=OuterRef("series_name"))

        breakdown_query = Experiment.objects.values("theory_driven") \
            .distinct() \
            .annotate(series_name=F("theory_driven"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_task(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__tasks__type=OuterRef("pk"))

        breakdown_query = TaskType.objects.values("name") \
            .distinct(). \
            annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_stimuli_category(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__stimuli__category=OuterRef("pk"))

        breakdown_query = StimulusCategory.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_modality(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__stimuli__modality=OuterRef("pk"))

        breakdown_query = ModalityType.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_phase(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__consciousness_measures__phase=OuterRef("pk"))

        breakdown_query = ConsciousnessMeasurePhaseType.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__consciousness_measures__type=OuterRef("pk"))

        breakdown_query = ConsciousnessMeasureType.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_type_of_consciousness(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__type_of_consciousness=OuterRef("series_name"))

        breakdown_query = Experiment.objects.values("type_of_consciousness") \
            .distinct() \
            .annotate(series_name=F("type_of_consciousness"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_technique(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__techniques=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")
        breakdown_query = Technique.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_measure(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__measures__type=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = MeasureType.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs
