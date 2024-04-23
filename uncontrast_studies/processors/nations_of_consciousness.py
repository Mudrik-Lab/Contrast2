from django.db.models import Func, F, Count, QuerySet

from uncontrast_studies.models import UnConExperiment
from uncontrast_studies.processors.base import BaseProcessor


class NationOfConsciousnessDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)

    def process(self):
        """
        do a transpose "experiment per country in study" with unnest on the array field
        aggregate on country and theory relation


        """
        # First we'll get an experiment per country
        experiments_by_countries = self.get_queryset()

        aggregate = self.aggregate(experiments_by_countries)

        return aggregate

    def get_queryset(self):
        filtered_qs = self.experiments

        experiments_by_countries_and_theories = (
            filtered_qs.select_related("study")
            .values("id", "study", "significance")
            .annotate(country=Func(F("study__countries"), function="unnest"))
        )
        return experiments_by_countries_and_theories

    def aggregate(self, queryset):
        # having "values" before annotate with count results in a "select *, count(1) from .. GROUP BY
        if self.is_csv:
            ids = queryset.values_list("id", flat=True)
            return set(ids)

        countries_total = (
            queryset.values("country")
            .annotate(value=Count("id", distinct=False))
            .filter(value__gt=self.min_number_of_experiments)
            .order_by("country")
        )
        countries_total_dict = {item["country"]: item["value"] for item in list(countries_total)}

        aggregated_qs = (
            queryset.values("country", "significance")
            .annotate(value=Count("id"))
            .filter(value__gt=self.min_number_of_experiments)
            .order_by("-value", "country")
        )
        retval = []
        for series in aggregated_qs:
            series["total"] = countries_total_dict[series["country"]]
            retval.append(series)
        return retval
