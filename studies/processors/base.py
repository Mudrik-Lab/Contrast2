from django.db.models import QuerySet

from studies.models import Experiment


class BaseProcessor:
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        self.experiments: QuerySet[Experiment] = experiments
        min_number_of_experiments = kwargs.pop("min_number_of_experiments", 0)
        if min_number_of_experiments > 0:
            # so everything that explicitly sets a minimum it would be supported
            min_number_of_experiments = min_number_of_experiments - 1
        self.min_number_of_experiments = min_number_of_experiments

    def process(self):
        raise NotImplementedError()
