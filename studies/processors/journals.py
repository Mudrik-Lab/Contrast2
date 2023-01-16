from django.db.models import QuerySet

from studies.models import Experiment
from studies.processors.base import BaseProcessor


class JournalsGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)

    def process(self):
        pass
