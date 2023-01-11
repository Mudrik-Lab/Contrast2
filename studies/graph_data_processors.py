from typing import Union, List, Iterable

from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, Func, F, Count, OuterRef, Sum, Value
from django.db.models.functions import JSONObject

from studies.choices import InterpretationsChoices
from studies.models import Study, Experiment, Interpretation, Paradigm, Sample, Task, Stimulus, ConsciousnessMeasure, \
    Technique, Measure, FindingTag, MeasureType


class BaseProcessor:
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        self.experiments = experiments

    def process(self):
        raise NotImplementedError()


class AcrossTheYearsGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]

    def process(self):
        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def process_paradigm_family(self):
        experiments_subquery_by_breakdown = self.experiments.filter(paradigms__parent=OuterRef("pk"))

        breakdown_query = Paradigm.objects.filter(parent__isnull=True).values("name").distinct(
            "name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_paradigm(self):
        experiments_subquery_by_breakdown = self.experiments.filter(paradigms=OuterRef("pk"))
        breakdown_query = Paradigm.objects.filter(parent__isnull=False).values("name").distinct(
            "name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_population(self):
        experiments_subquery_by_breakdown = self.experiments.filter(samples=OuterRef("pk"))

        breakdown_query = Sample.objects.values("type__name").distinct(
            "type__name").annotate(series_name=F("type__name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag(self):
        experiments_subquery_by_breakdown = self.experiments.filter(finding_tags=OuterRef("pk"))

        breakdown_query = FindingTag.objects.values("type__name").distinct(
            "type__name").annotate(series_name=F("type__name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag_family(self):
        experiments_subquery_by_breakdown = self.experiments.filter(finding_tags=OuterRef("pk"))

        breakdown_query = FindingTag.objects.values("family__name").distinct(
            "family__name").annotate(series_name=F("family__name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_reporting(self):
        pass

    def process_task(self):
        experiments_subquery_by_breakdown = self.experiments.filter(tasks=OuterRef("pk"))

        breakdown_query = Task.objects.values("type__name").distinct(
            "type__name").annotate(series_name=F("type__name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_stimuli_category(self):
        pass

    def process_modality(self):
        experiments_subquery_by_breakdown = self.experiments.filter(stimuli=OuterRef("pk"))

        breakdown_query = Stimulus.objects.values("modality__name").distinct(
            "modality__name").annotate(series_name=F("modality__name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs


    def process_consciousness_measure_phase(self):

        experiments_subquery_by_breakdown = self.experiments.filter(consciousness_measures=OuterRef("pk"))

        breakdown_query = ConsciousnessMeasure.objects.values("consciousness_measures__phase__name").distinct(
            "consciousness_measures__phase__name").annotate(series_name=F("consciousness_measures__phase__name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = self.experiments.filter(consciousness_measures=OuterRef("pk"))

        breakdown_query = ConsciousnessMeasure.objects.values("consciousness_measures__type__name").distinct(
            "consciousness_measures__type__name").annotate(series_name=F("consciousness_measures__type__name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs


    def process_type_of_consciousness(self):
        pass


    def process_technique(self):
        experiments_subquery_by_breakdown = self.experiments.filter(techniques=OuterRef("pk"))
        breakdown_query = Technique.objects.values("name").distinct(
            "name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_measure(self):
        experiments_subquery_by_breakdown = self.experiments.filter(measures__type=OuterRef("pk"))

        breakdown_query = MeasureType.objects.values("name").distinct(
            "name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs



    def _aggregate_query_by_breakdown(self, queryset: QuerySet, filtered_subquery: QuerySet):
        # Hopefully this is generic enough to be reused
        subquery = filtered_subquery.annotate(year=F("study__year")) \
            .values("year") \
            .order_by("year") \
            .annotate(experiment_count=Count("id")) \
            .annotate(data=JSONObject(year=F("year"), value=F("experiment_count"))) \
            .values_list("data")

        qs = queryset \
            .values("series_name").annotate(series=ArraySubquery(subquery)) \
            .values("series_name", "series")\
            .order_by("series_name")
        return qs


class NationOfConsciousnessDataProcessor(BaseProcessor):
    def process(self):
        """
        do a transpose "experiment per country in study" with unset on the array field
        aggregate on country and theory relation


        """
        # First we'll get an experiment per country
        experiments_by_countries_and_theories = self.resolve_queryset()

        aggregate = self.aggregate(experiments_by_countries_and_theories)

        return aggregate

    def resolve_queryset(self):
        experiments_by_countries_and_theories = Interpretation.objects \
            .filter(type=InterpretationsChoices.PRO,
                    experiment__in=self.experiments) \
            .select_related("experiment", "experiment__study") \
            .values("experiment", "experiment__study", "theory__parent__name") \
            .annotate(country=Func(F("experiment__study__countries"),
                                   function='unnest'))
        return experiments_by_countries_and_theories

    def aggregate(self, qs):
        # having "values" before annotate with count results in a "select *, count(1) from .. GROUP BY
        return qs.values("country", "theory__parent__name").annotate(count=Count("id")).order_by("-count", "country")
