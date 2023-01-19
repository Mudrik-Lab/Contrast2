from django.db.models import QuerySet, Count, F

from studies.choices import InterpretationsChoices
from studies.models import Experiment, Interpretation
from studies.processors.base import BaseProcessor


class JournalsGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        self.theory = kwargs.pop("theory")

        super().__init__(experiments=experiments, **kwargs)

    def process(self):
        relevant_experiments = self.get_queryset()

        aggregate = self.aggregate(relevant_experiments)

        return aggregate

    def get_queryset(self):
        experiments_by_theory = Interpretation.objects \
            .filter(type=InterpretationsChoices.PRO,
                    theory__parent__name=self.theory,
                    experiment__in=self.experiments) \
            .select_related("experiment", "experiment__study") \
            .values("experiment", "experiment__study") \
            .annotate(journal=F("experiment__study__abbreviated_source_title"))
        return experiments_by_theory

    def aggregate(self, qs):
        # having "values" before annotate with count results in a "select *, count(1) from .. GROUP BY
        return qs.values("journal").annotate(count=Count("id")).order_by("-count", "journal")
