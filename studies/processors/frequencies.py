from django.db.models import QuerySet

from studies.models import Experiment
from studies.processors.base import BaseProcessor


class FrequenciesGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]

    def process(self):
        pass
