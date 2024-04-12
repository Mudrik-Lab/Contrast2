from typing import List

from django.db.models import QuerySet

from contrast_api.utils import cast_as_boolean
from uncontrast_studies.models import UnConExperiment


class BaseProcessor:
    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        self.experiments: QuerySet[UnConExperiment] = experiments
        min_number_of_experiments = int(kwargs.pop("min_number_of_experiments", ["0"])[0])
        if min_number_of_experiments > 0:
            # so everything that explicitly sets a minimum it would be supported, with a gt query
            min_number_of_experiments = min_number_of_experiments - 1
        self.min_number_of_experiments = min_number_of_experiments

        self.is_csv = cast_as_boolean(kwargs.pop("is_csv", [False])[0])

    def process(self):
        raise NotImplementedError()

    def accumulate_inner_series_values_and_filter(self, data, min_count: int) -> List:
        accumulated_data = []
        accumulated = 0
        for dataset in data:
            accumulated = accumulated + dataset["value"]
            new_dataset = dict(**dataset)
            new_dataset.update({"value": accumulated})
            accumulated_data.append(new_dataset)
        if accumulated > min_count:
            return accumulated_data
        else:
            return []

    def accumulate_total_from_series(self, data) -> int:
        return sum([series["value"] for series in data])
