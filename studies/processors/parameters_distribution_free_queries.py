import itertools

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import Func, F, Count, QuerySet, OuterRef

from studies.models import (
    Interpretation,
    Experiment,
    MeasureType,
    Technique,
    ConsciousnessMeasureType,
    ConsciousnessMeasurePhaseType,
    ModalityType,
    TaskType,
    FindingTagFamily,
    FindingTagType,
    Sample,
    Paradigm,
)
from studies.models.stimulus import StimulusCategory
from studies.processors.base import BaseProcessor


class ParametersDistributionFreeQueriesDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)

        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]
        self.interpretations_types = kwargs.pop("interpretations_types", [])
        self.interpretation_theories = kwargs.pop("interpretation_theories", [])
        self.techniques = kwargs.pop("techniques", [])
        self.paradigms = kwargs.pop("paradigms", [])
        self.paradigm_families = kwargs.pop("paradigm_families", [])
        self.stimuli_categories = kwargs.pop("stimuli_categories", [])
        self.stimuli_modalities = kwargs.pop("stimuli_modalities", [])
        self.populations = kwargs.pop("populations", [])
        self.measures = kwargs.pop("measures", [])
        self.consciousness_measure_phases = kwargs.pop("consciousness_measure_phases", [])
        self.consciousness_measure_types = kwargs.pop("consciousness_measure_types", [])
        self.finding_tags_families = kwargs.pop("finding_tags_families", [])
        self.finding_tags_types = kwargs.pop("finding_tags_types", [])
        self.theory_driven = kwargs.pop("theory_driven", [])
        self.types = kwargs.pop("types", [])
        self.tasks = kwargs.pop("tasks", [])

    def process(self):
        """
        do a transpose "experiment per country in study" with unnest on the array field
        aggregate on country and theory relation


        """
        # First we'll filter the available experiments
        self.filtered_experiments = self.get_queryset()

        process_func = getattr(self, f"process_{self.breakdown}")
        return process_func()

    def get_queryset(self):
        queryset = self.experiments
        if len(self.interpretations_types):
            if len(self.interpretation_theories):
                queryset = queryset.filter(
                    id__in=Interpretation.objects.filter(
                        type__in=self.interpretations_types, theory__parent_id__in=self.interpretation_theories
                    ).values_list("experiment_id", flat=True)
                )
            else:
                queryset = queryset.filter(
                    id__in=Interpretation.objects.filter(type__in=self.interpretations_types).values_list(
                        "experiment_id", flat=True
                    )
                )
        if len(self.techniques):
            queryset = queryset.filter(techniques__id__in=self.techniques)

        if len(self.paradigms):
            queryset = queryset.filter(paradigms__id__in=self.paradigms)

        if len(self.paradigm_families):
            queryset = queryset.filter(paradigms__parent__id__in=self.paradigm_families)

        if len(self.stimuli_categories):
            queryset = queryset.filter(stimuli__category__id__in=self.stimuli_categories)

        if len(self.stimuli_modalities):
            queryset = queryset.filter(stimuli__modality__id__in=self.stimuli_modalities)

        if len(self.populations):
            queryset = queryset.filter(samples__type__in=self.populations)

        if len(self.measures):
            queryset = queryset.filter(measures__type__id__in=self.measures)

        if len(self.consciousness_measure_phases):
            queryset = queryset.filter(consciousness_measures__phase__id__in=self.consciousness_measure_phases)

        if len(self.consciousness_measure_types):
            queryset = queryset.filter(consciousness_measures__type__id__in=self.consciousness_measure_types)

        if len(self.finding_tags_families):
            queryset = queryset.filter(finding_tags__family__id__in=self.finding_tags_families)

        if len(self.finding_tags_types):
            queryset = queryset.filter(finding_tags__type__id__in=self.finding_tags_types)

        if len(self.theory_driven):
            # Note how this works by theory
            queryset = queryset.filter(theory_driven__in=self.theory_driven)

        if len(self.types):
            queryset = queryset.filter(type__in=self.types)

        if len(self.tasks):
            queryset = queryset.filter(tasks__type__id__in=self.tasks)

        return queryset

    def process_paradigm_family(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__paradigms__parent__name=OuterRef("name"))
            .values("experiment")
        )

        breakdown_query = (
            Paradigm.objects.filter(parent__isnull=True).order_by("name").values("name").distinct("name").annotate(series_name=F("name"))

        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_paradigm(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__paradigms__name=OuterRef("name"))
            .values("experiment")
        )

        breakdown_query = (
            Paradigm.objects.filter(parent__isnull=False).order_by("name").values("name").distinct("name").annotate(series_name=F("name"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_population(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__samples__type=OuterRef("series_name"))
            .values("experiment")
        )

        breakdown_query = Sample.objects.values("type").distinct().annotate(series_name=F("type"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__finding_tags__type=OuterRef("pk"))
            .filter(experiment__finding_tags__is_NCC=True)
            .values("experiment")
        )

        breakdown_query = FindingTagType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_finding_tag_family(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__finding_tags__family=OuterRef("pk"))
            .filter(experiment__finding_tags__is_NCC=True)
            .values("experiment")
        )

        breakdown_query = FindingTagFamily.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_reporting(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__is_reporting=OuterRef("series_name"))
            .values("experiment")
        )

        breakdown_query = Experiment.objects.values("is_reporting").distinct().annotate(series_name=F("is_reporting"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_theory_driven(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__theory_driven=OuterRef("series_name"))
            .values("experiment")
        )

        breakdown_query = Experiment.objects.values("theory_driven").distinct().annotate(series_name=F("theory_driven"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_task(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__tasks__type=OuterRef("pk"))
            .values("experiment")
        )

        breakdown_query = TaskType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_stimuli_category(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__stimuli__category=OuterRef("pk"))
            .values("experiment")
        )

        breakdown_query = StimulusCategory.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_modality(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__stimuli__modality=OuterRef("pk"))
            .values("experiment")
        )

        breakdown_query = ModalityType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_phase(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__consciousness_measures__phase=OuterRef("pk"))
            .values("experiment")
        )

        breakdown_query = (
            ConsciousnessMeasurePhaseType.objects.values("name").distinct().annotate(series_name=F("name"))
        )

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_consciousness_measure_type(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__consciousness_measures__type=OuterRef("pk"))
            .values("experiment")
        )

        breakdown_query = ConsciousnessMeasureType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_type_of_consciousness(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__type_of_consciousness=OuterRef("series_name"))
            .values("experiment")
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
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__techniques=OuterRef("pk"))
            .values("experiment")
        )

        breakdown_query = Technique.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def process_measure(self):
        experiments_subquery_by_breakdown = (
            Interpretation.objects.filter(experiment__in=self.filtered_experiments)
            .filter(experiment__measures__type=OuterRef("pk"))
            .values("experiment")
        )

        breakdown_query = MeasureType.objects.values("name").distinct().annotate(series_name=F("name"))

        qs = self._aggregate_query_by_breakdown(breakdown_query, experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, queryset: QuerySet, filtered_subquery: QuerySet):
        # Hopefully this is generic enough to be reused

        if self.is_csv:
            ids = queryset.annotate(
                experiments=ArraySubquery(filtered_subquery.values_list("experiment_id"))
            ).values_list("experiments", flat=True)
            return set(list(itertools.chain.from_iterable(ids)))

        annotated_subquery = filtered_subquery.annotate(experiment_count=Count("id", distinct=True))

        ids_subquery = annotated_subquery.order_by("experiment").values_list("experiment")

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
