from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Func, Subquery, Count, Sum, IntegerField
from django.db.models.functions import JSONObject

from studies.choices import InterpretationsChoices
from studies.models import Experiment, Paradigm, Interpretation, Sample, FindingTagType, FindingTagFamily, TaskType, \
    ModalityType, ConsciousnessMeasurePhaseType, ConsciousnessMeasureType, Technique, MeasureType, Theory
from studies.models.stimulus import StimulusCategory
from studies.processors.base import BaseProcessor


class ParametersDistributionBarGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]
        theory = kwargs.pop("theory")
        self.theory = None
        if len(theory):
            theory_reference = theory[0]
            try:
                theory = Theory.objects.get(name=theory_reference)
            except Theory.DoesNotExist:
                theory = Theory.objects.get(id=theory_reference)
            self.theory = theory

    def process(self):
        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def process_paradigm_family(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__paradigms__parent=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = Paradigm.objects.filter(parent__isnull=True).values("name").distinct(
        ).annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_paradigm(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__paradigms=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = Paradigm.objects.filter(parent__isnull=False).values("name")\
            .distinct()\
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_population(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__samples=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = Sample.objects.values("type")\
            .distinct().\
            annotate(series_name=F("type"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__finding_tags__type=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = FindingTagType.objects.values("name")\
            .distinct()\
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag_family(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__finding_tags__family=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = FindingTagFamily.objects.values("name")\
            .distinct()\
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_reporting(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__is_reporting=OuterRef("series_name")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = Experiment.objects.values("is_reporting")\
            .distinct()\
            .annotate(series_name=F("is_reporting"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_theory_driven(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__theory_driven=OuterRef("series_name")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = Experiment.objects.values("theory_driven")\
            .distinct()\
            .annotate(series_name=F("theory_driven"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_task(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__tasks__type=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = TaskType.objects.values("name")\
            .distinct().\
            annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_stimuli_category(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__stimuli__category=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = StimulusCategory.objects.values("name")\
            .distinct()\
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_modality(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__stimuli__modality=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = ModalityType.objects.values("name")\
            .distinct()\
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_phase(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__consciousness_measures__phase=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = ConsciousnessMeasurePhaseType.objects.values("name")\
            .distinct()\
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__consciousness_measures__type=OuterRef("pk")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = ConsciousnessMeasureType.objects.values("name")\
            .distinct()\
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_type_of_consciousness(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__type_of_consciousness=OuterRef("series_name")) \
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = Experiment.objects.values("type_of_consciousness")\
            .distinct()\
            .annotate(series_name=F("type_of_consciousness"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_technique(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__techniques=OuterRef("pk"))\
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")
        breakdown_query = Technique.objects.values("name")\
            .distinct()\
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_measure(self):
        experiments_subquery_by_breakdown = Interpretation.objects.filter(experiment__in=self.experiments) \
            .filter(experiment__measures__type=OuterRef("pk"))\
            .annotate(relation_type=F("type")) \
            .values("experiment", "relation_type")

        breakdown_query = MeasureType.objects.values("name")\
            .distinct()\
            .annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, queryset: QuerySet, filtered_subquery: QuerySet):
        # Hopefully this is generic enough to be reused
        if self.theory is not None:
            filtered_subquery = filtered_subquery.filter(theory__parent=self.theory)
        by_relation_type_subquery = filtered_subquery.filter(
            relation_type__in=[InterpretationsChoices.PRO, InterpretationsChoices.CHALLENGES]).values(
            "relation_type").order_by("-relation_type").annotate(experiment_count=Count("id", distinct=True))
        subquery = by_relation_type_subquery \
            .annotate(data=JSONObject(key=F("relation_type"), value=F("experiment_count"))) \
            .values_list("data")

        ids_subquery = by_relation_type_subquery \
            .order_by("experiment") \
            .values_list("experiment")

        qs = queryset \
            .values("series_name").annotate(series=ArraySubquery(subquery)) \
            .annotate(ids_list=ArraySubquery(ids_subquery)) \
            .annotate(totals=Func(F('ids_list'), function='CARDINALITY')) \
            .annotate(field_len=Func(F('series'), function='CARDINALITY')) \
            .filter(field_len__gt=0) \
            .filter(totals__gt=self.min_number_of_experiments)\
            .values("series_name", "series", "totals") \
            .order_by("-totals", "series_name")
        # Note we're filtering out empty timeseries with the cardinality option
        # TODO order by total of inner values
        return qs
