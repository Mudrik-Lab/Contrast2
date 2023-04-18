from django.db.models import Func, F, Count

from studies.choices import InterpretationsChoices
from studies.models import Interpretation
from studies.processors.base import BaseProcessor


class NationOfConsciousnessDataProcessor(BaseProcessor):
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
