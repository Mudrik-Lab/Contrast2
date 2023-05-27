from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Count, Func, Window, Sum, Subquery
from django.db.models.functions import JSONObject

from studies.models import Experiment, Paradigm, Sample, FindingTagType, FindingTagFamily, TaskType, ModalityType, \
    ConsciousnessMeasurePhaseType, ConsciousnessMeasureType, Technique, MeasureType
from studies.models.stimulus import StimulusCategory
from studies.processors.base import BaseProcessor


class TrendsOverYearsGraphDataProcessor(BaseProcessor):
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
        experiments_subquery_by_breakdown = self.experiments.filter(samples__type=OuterRef("type"))

        breakdown_query = Sample.objects.values("type").distinct(
        ).annotate(series_name=F("type"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag(self):
        experiments_subquery_by_breakdown = self.experiments.filter(finding_tags__type=OuterRef("pk"))

        breakdown_query = FindingTagType.objects.values("name").distinct(
            "name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag_family(self):
        experiments_subquery_by_breakdown = self.experiments.filter(finding_tags__family=OuterRef("pk"))

        breakdown_query = FindingTagFamily.objects.values("name").distinct(
            "name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_reporting(self):
        experiments_subquery_by_breakdown = self.experiments.filter(is_reporting=OuterRef("series_name"))

        breakdown_query = Experiment.objects.values("is_reporting").distinct(
            "is_reporting").annotate(series_name=F("is_reporting"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_theory_driven(self):
        experiments_subquery_by_breakdown = self.experiments.filter(theory_driven=OuterRef("series_name"))

        breakdown_query = Experiment.objects.values("theory_driven").distinct(
            "theory_driven").annotate(series_name=F("theory_driven"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_task(self):
        experiments_subquery_by_breakdown = self.experiments.filter(tasks__type=OuterRef("pk"))

        breakdown_query = TaskType.objects.values("name").distinct(
            "name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_stimuli_category(self):
        experiments_subquery_by_breakdown = self.experiments.filter(stimuli__category=OuterRef("pk"))

        breakdown_query = StimulusCategory.objects.values("name").distinct(
            "name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_modality(self):
        experiments_subquery_by_breakdown = self.experiments.filter(stimuli__modality=OuterRef("pk"))

        breakdown_query = ModalityType.objects.values("name").distinct(
            "name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_phase(self):
        experiments_subquery_by_breakdown = self.experiments.filter(consciousness_measures__phase=OuterRef("pk"))

        breakdown_query = ConsciousnessMeasurePhaseType.objects.values("name").distinct(
            "name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = self.experiments.filter(consciousness_measures__type=OuterRef("pk"))

        breakdown_query = ConsciousnessMeasureType.objects.values("name").distinct(
            "name").annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_type_of_consciousness(self):
        experiments_subquery_by_breakdown = self.experiments.filter(type_of_consciousness=OuterRef("series_name"))

        breakdown_query = Experiment.objects.values("type_of_consciousness").distinct(
            "type_of_consciousness").annotate(series_name=F("type_of_consciousness"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

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
        if self.is_csv:
            return queryset.annotate(experiments=ArraySubquery(filtered_subquery.values_list("id"))).values_list("experiments", flat=True)
        subquery = filtered_subquery.annotate(year=F("study__year")) \
            .values("year") \
            .order_by("year") \
            .annotate(experiment_count=Count("id", distinct=True)) \
            .annotate(data=JSONObject(year=F("year"), value=F("experiment_count"))) \
            .values_list("data")

        qs = queryset \
            .values("series_name").annotate(series=ArraySubquery(subquery)) \
            .annotate(field_len=Func(F('series'), function='CARDINALITY')) \
            .filter(field_len__gt=0) \
            .values("series_name", "series") \
            .order_by("series_name")
        # Note we're filtering out empty timeseries with the cardinality option
        retval = []
        earliest_year = None
        for series_data in list(qs):

            series = self.accumulate_inner_series_values_and_filter(series_data["series"],
                                                                    self.min_number_of_experiments)
            if len(series):
                earliest_year_in_series = series_data["series"][0]["year"]
                if earliest_year is None or earliest_year_in_series < earliest_year:
                    earliest_year = earliest_year_in_series
                retval.append(dict(series_name=series_data["series_name"], series=series))
        if earliest_year is not None:
            for line in retval:
                if line["series"][0]["year"] > earliest_year:
                    # todo check if I can really insert like that
                    line["series"].insert(0, dict(year=earliest_year, value=0))
        return retval
