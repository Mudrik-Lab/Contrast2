from django.db.models import QuerySet

from studies.models import Experiment
from studies.processors.base import BaseProcessor


class FrequenciesGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[Experiment], **kwargs):
        experiments = experiments.filter(finding_tags__family__name="Frequency")
        super().__init__(experiments=experiments, **kwargs)
        breakdown = kwargs.pop("breakdown")
        self.breakdown = breakdown[0]
        sort_first = kwargs.pop("sort_first", ["earliest"])
        self.sort_first = sort_first[0]
        self.theory = kwargs.pop("theory")[0]
        self.is_theory_driven_only = kwargs.pop("is_theory_driven", [False])[0]
        self.tags_types = kwargs.pop("tags_types")

    def process(self):
        pass
