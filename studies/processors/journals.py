import itertools

from django.db.models import QuerySet, Count, F

from studies.choices import InterpretationsChoices
from studies.models import Experiment, Interpretation, Theory
from studies.processors.base import BaseProcessor


class JournalsGraphDataProcessor(BaseProcessor):
    """
    This expects as input the ID of the parent theory..
    """

    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)

        theory = kwargs.pop("theory", [])
        self.theory = None
        if len(theory):
            theory_reference = theory[0]
            try:
                theory = Theory.objects.get(name__iexact=theory_reference)
            except Theory.DoesNotExist:
                theory = Theory.objects.get(id=theory_reference)
            self.theory = theory

        super().__init__(experiments=experiments, **kwargs)

    def process(self):
        relevant_experiments = self.get_queryset()

        aggregate = self.aggregate(relevant_experiments)

        return aggregate

    def get_queryset(self):
        queryset = Interpretation.objects.all()
        if self.theory is not None:
            queryset = queryset.filter(
                theory__parent_id=self.theory)
        experiments_by_theory = queryset \
            .filter(type=InterpretationsChoices.PRO,
                    experiment__in=self.experiments) \
            .select_related("experiment", "experiment__study") \
            .values("experiment", "experiment__study") \
            .annotate(journal=F("experiment__study__abbreviated_source_title"))
        return experiments_by_theory

    def aggregate(self, queryset):
        if self.is_csv:
            ids = queryset.values_list(
                "experiment_id", flat=True)
            return set(ids)
        # having "values" before annotate with count results in a "select *, count(1) from .. GROUP BY

        return queryset.values("journal") \
            .annotate(count=Count("experiment_id", distinct=True)) \
            .filter(count__gt=self.min_number_of_experiments) \
            .annotate(value=F("count"),
                      key=F("journal")) \
            .values("value", "key") \
            .order_by("-value", "key")
