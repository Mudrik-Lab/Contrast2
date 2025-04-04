import itertools

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Func, Count
from django.db.models.functions import JSONObject

from contrast_api.choices import InterpretationsChoices
from studies.models import (
    Experiment,
    Paradigm,
    Sample,
    FindingTagType,
    FindingTagFamily,
    TaskType,
    ModalityType,
    ConsciousnessMeasurePhaseType,
    ConsciousnessMeasureType,
    Technique,
    MeasureType,
    AggregatedInterpretation,
)
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
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO,
            experiment__in=self.experiments,
            experiment__paradigms__parent=OuterRef("pk"),
        )

        breakdown_query = (
            Paradigm.objects.filter(parent__isnull=True).values("name").distinct().annotate(series_name=F("name"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_paradigm(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO,
            experiment__in=self.experiments,
            experiment__paradigms__name=OuterRef("name"),
        )

        breakdown_query = (
            Paradigm.objects.filter(parent__isnull=False).values("name").distinct().annotate(series_name=F("name"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_population(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO, experiment__in=self.experiments, experiment__samples__type=OuterRef("type")
        )

        breakdown_query = Sample.objects.values("type").order_by("type").distinct().annotate(series_name=F("type"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO,
            experiment__in=self.experiments,
            experiment__finding_tags__type=OuterRef("pk"),
            experiment__finding_tags__is_NCC=True,
        )

        breakdown_query = FindingTagType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag_family(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO,
            experiment__in=self.experiments,
            experiment__finding_tags__is_NCC=True,
            experiment__finding_tags__family=OuterRef("pk"),
        )

        breakdown_query = FindingTagFamily.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_reporting(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO,
            experiment__in=self.experiments,
            experiment__is_reporting=OuterRef("series_name"),
        )

        breakdown_query = Experiment.objects.values("is_reporting").distinct().annotate(series_name=F("is_reporting"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_theory_driven(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO,
            experiment__in=self.experiments,
            experiment__theory_driven=OuterRef("series_name"),
        )

        breakdown_query = Experiment.objects.values("theory_driven").distinct().annotate(series_name=F("theory_driven"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_task(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO, experiment__in=self.experiments, experiment__tasks__type=OuterRef("pk")
        )

        breakdown_query = TaskType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_stimuli_category(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO,
            experiment__in=self.experiments,
            experiment__stimuli__category=OuterRef("pk"),
        )

        breakdown_query = StimulusCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_modality(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO,
            experiment__in=self.experiments,
            experiment__stimuli__modality=OuterRef("pk"),
        )

        breakdown_query = ModalityType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_phase(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO,
            experiment__in=self.experiments,
            experiment__consciousness_measures__phase=OuterRef("pk"),
        )

        breakdown_query = (
            ConsciousnessMeasurePhaseType.objects.values("name").distinct().annotate(series_name=F("name"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO,
            experiment__in=self.experiments,
            experiment__consciousness_measures__type=OuterRef("pk"),
        )

        breakdown_query = ConsciousnessMeasureType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_type_of_consciousness(self):
        experiments_subquery_by_breakdown = AggregatedInterpretation.objects.filter(
            type=InterpretationsChoices.PRO,
            experiment__in=self.experiments,
            experiment__type_of_consciousness=OuterRef("series_name"),
        )

        breakdown_query = (
            Experiment.objects.values("type_of_consciousness")
            .distinct()
            .annotate(series_name=F("type_of_consciousness"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_technique(self):
        experiments_subquery_by_breakdown = (
            AggregatedInterpretation.objects.filter(
                type=InterpretationsChoices.PRO, experiment__in=self.experiments, experiment__techniques=OuterRef("pk")
            )
            .annotate(relation_type=F("type"))
            .values("experiment", "relation_type")
        )
        breakdown_query = Technique.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_measure(self):
        experiments_subquery_by_breakdown = (
            AggregatedInterpretation.objects.filter(
                type=InterpretationsChoices.PRO,
                experiment__in=self.experiments,
                experiment__measures__type=OuterRef("pk"),
            )
            .annotate(relation_type=F("type"))
            .values("experiment", "relation_type")
        )

        breakdown_query = MeasureType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, queryset: QuerySet, filtered_subquery: QuerySet):
        theory_subquery = filtered_subquery.values("parent_theory_acronyms").annotate(
            experiment_count=Count("id", distinct=True)
        )

        if self.is_csv:
            ids = queryset.annotate(
                experiments=ArraySubquery(filtered_subquery.values_list("experiment_id"))
            ).values_list("experiments", flat=True)
            return set(list(itertools.chain.from_iterable(ids)))

        subquery = (
            theory_subquery.order_by("-experiment_count")
            .filter(experiment_count__gt=self.min_number_of_experiments)
            .annotate(data=JSONObject(key=F("parent_theory_acronyms"), value=F("experiment_count")))
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
