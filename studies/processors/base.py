from django.db.models import QuerySet

from studies.models import Experiment


class BaseProcessor:
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        self.experiments: QuerySet[Experiment] = experiments

    def process(self):
        raise NotImplementedError()
