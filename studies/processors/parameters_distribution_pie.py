from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Func, Subquery, Count, Sum, IntegerField, Q
from django.db.models.functions import JSONObject

from contrast_api.orm_helpers import SubqueryCount
from studies.choices import InterpretationsChoices
from studies.models import Experiment, Paradigm, Interpretation, Sample, FindingTagType, FindingTagFamily, TaskType, \
    ModalityType, ConsciousnessMeasurePhaseType, ConsciousnessMeasureType, Technique, MeasureType, \
    AggregatedInterpretation
from studies.models.stimulus import StimulusCategory
from studies.processors.base import BaseProcessor


class ParametersDistributionPieGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]

    def process(self):
        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def process_paradigm_family(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__paradigms__parent=OuterRef("pk"))

        breakdown_query = Paradigm.objects.filter(parent__isnull=True).values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_paradigm(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__paradigms=OuterRef("pk"))

        breakdown_query = Paradigm.objects.filter(parent__isnull=False).values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_population(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__samples__type=OuterRef("type"))

        breakdown_query = Sample.objects.values("type") \
            .order_by("type") \
            .distinct() \
            .annotate(series_name=F("type"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__finding_tags__type=OuterRef("pk"))

        breakdown_query = FindingTagType.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag_family(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__finding_tags__family=OuterRef("pk"))

        breakdown_query = FindingTagFamily.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_reporting(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__is_reporting=OuterRef("series_name"))

        breakdown_query = Experiment.objects.values("is_reporting") \
            .distinct() \
            .annotate(series_name=F("is_reporting"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_theory_driven(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__theory_driven=OuterRef("series_name"))

        breakdown_query = Experiment.objects.values("theory_driven") \
            .distinct() \
            .annotate(series_name=F("theory_driven"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_task(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__tasks__type=OuterRef("pk"))

        breakdown_query = TaskType.objects.values("name") \
            .distinct(). \
            annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_stimuli_category(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__stimuli__category=OuterRef("pk"))

        breakdown_query = StimulusCategory.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_modality(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__stimuli__modality=OuterRef("pk"))

        breakdown_query = ModalityType.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_phase(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__consciousness_measures__phase=OuterRef("pk"))

        breakdown_query = ConsciousnessMeasurePhaseType.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__consciousness_measures__type=OuterRef("pk"))

        breakdown_query = ConsciousnessMeasureType.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_type_of_consciousness(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__type_of_consciousness=OuterRef("series_name"))

        breakdown_query = Experiment.objects.values("type_of_consciousness") \
            .distinct() \
            .annotate(series_name=F("type_of_consciousness"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_technique(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__techniques=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")
        breakdown_query = Technique.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_measure(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(type=InterpretationsChoices.PRO) \
            .filter(experiment__in=self.experiments) \
            .filter(experiment__measures__type=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = MeasureType.objects.values("name") \
            .distinct() \
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, queryset: QuerySet, filtered_subquery: QuerySet):
        theory_subquery = filtered_subquery.values("parent_theory_names") \
            .annotate(experiment_count=Count("id", distinct=True))
        subquery = theory_subquery \
            .order_by("-experiment_count") \
            .filter(experiment_count__gt=self.min_number_of_experiments) \
            .annotate(data=JSONObject(key=F("parent_theory_names"), value=F("experiment_count"))) \
            .values_list("data")

        ids_subquery = theory_subquery \
            .order_by("experiment") \
            .values_list("experiment_id")

        qs = queryset \
            .values("series_name").annotate(series=ArraySubquery(subquery)) \
            .annotate(field_len=Func(F('series'), function='CARDINALITY')) \
            .annotate(value=SubqueryCount(ids_subquery)) \
            .filter(field_len__gt=0) \
            .filter(value__gt=0) \
            .values("series_name", "series", "value") \
            .order_by("-value", "series_name")
        # Note we're filtering out empty timeseries with the cardinality option
        # TODO order by total of inner values
        return qs
