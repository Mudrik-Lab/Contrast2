from django.db.models import Func, F, Count, QuerySet

from studies.choices import InterpretationsChoices
from studies.models import Interpretation, Theory, Experiment
from studies.processors.base import BaseProcessor


class NationOfConsciousnessDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        theories_reference = kwargs.pop("theory", [])
        self.all_theories = Theory.objects.filter(parent__isnull=True)
        self.theories = None
        if len(theories_reference):
            theories = Theory.objects.filter(name__in=theories_reference)
            if not len(theories):
                theories = Theory.objects.filter(id__in=theories_reference)

            self.theories = theories
        if self.theories is None:
            # case is ALL
            self.theories = self.all_theories

    def process(self):
        """
        do a transpose "experiment per country in study" with unnest on the array field
        aggregate on country and theory relation


        """
        # First we'll get an experiment per country
        experiments_by_countries_and_theories = self.get_queryset()

        aggregate = self.aggregate(experiments_by_countries_and_theories)

        return aggregate

    def get_queryset(self):
        filtered_qs = Interpretation.objects.filter(type=InterpretationsChoices.PRO, experiment__in=self.experiments)

        experiments_by_countries_and_theories = (
            filtered_qs.select_related("experiment", "experiment__study")
            .values("experiment", "experiment__study", "theory__parent__name")
            .annotate(country=Func(F("experiment__study__countries"), function="unnest"))
        )
        return experiments_by_countries_and_theories

    def aggregate(self, queryset):
        # having "values" before annotate with count results in a "select *, count(1) from .. GROUP BY
        if self.is_csv:
            ids = queryset.values_list("experiment_id", flat=True)
            return set(ids)

        countries_total = (
            queryset.values("country")
            .annotate(value=Count("experiment_id", distinct=False))
            .filter(value__gt=self.min_number_of_experiments)
            .order_by("country")
        )
        countries_total_dict = {item["country"]: item["value"] for item in list(countries_total)}

        aggregated_qs = (
            queryset.filter(theory__parent__in=self.theories)
            .values("country", "theory__parent__name")
            .annotate(value=Count("id"))
            .filter(value__gt=self.min_number_of_experiments)
            .order_by("-value", "country")
        )
        retval = []
        for series in aggregated_qs:
            series["total"] = countries_total_dict[series["country"]]
            retval.append(series)
        return retval
