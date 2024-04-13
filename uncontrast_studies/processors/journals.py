from django.db.models import QuerySet, Count, F

from uncontrast_studies.models import UnConExperiment
from uncontrast_studies.processors.base import BaseProcessor


class JournalsGraphDataProcessor(BaseProcessor):
    """
    This expects as input the ID of the parent theory..
    """

    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)

    def process(self):
        relevant_experiments = self.get_queryset()

        aggregate = self.aggregate(relevant_experiments)

        return aggregate

    def get_queryset(self):
        queryset = self.experiments
        experiments = (
            queryset.select_related("study")
            .values("id", "study")
            .annotate(journal=F("study__abbreviated_source_title"))
        )
        return experiments

    def aggregate(self, queryset):
        if self.is_csv:
            ids = queryset.values_list("id", flat=True)
            return set(ids)
        # having "values" before annotate with count results in a "select *, count(1) from .. GROUP BY

        return (
            queryset.values("journal")
            .annotate(count=Count("id", distinct=True))
            .filter(count__gt=self.min_number_of_experiments)
            .annotate(value=F("count"), key=F("journal"))
            .values("value", "key")
            .order_by("-value", "key")
        )
