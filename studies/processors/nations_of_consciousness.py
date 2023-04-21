from django.db.models import Func, F, Count, QuerySet

from studies.choices import InterpretationsChoices
from studies.models import Interpretation, Theory, Experiment
from studies.processors.base import BaseProcessor


class NationOfConsciousnessDataProcessor(BaseProcessor):

    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super(NationOfConsciousnessDataProcessor, self).__init__(experiments)
        theories_reference = kwargs.pop("theory")
        self.theories = None
        if len(theories_reference):

            theories = Theory.objects.filter(name__in=theories_reference)
            if not len(theories):
                theories = Theory.objects.filter(id__in=theories_reference)

            self.theories = theories

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
                    theory__parent__in=self.theories,
                    experiment__in=self.experiments) \
            .select_related("experiment", "experiment__study") \
            .values("experiment", "experiment__study", "theory__parent__name") \
            .annotate(country=Func(F("experiment__study__countries"),
                                   function='unnest'))
        return experiments_by_countries_and_theories

    def aggregate(self, qs):
        # having "values" before annotate with count results in a "select *, count(1) from .. GROUP BY
        return qs.values("country", "theory__parent__name")\
            .annotate(count=Count("id"))\
            .filter(count__gt=self.min_number_of_experiments)\
            .order_by("-count", "country")
