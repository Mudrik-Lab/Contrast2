import itertools

from django.contrib.postgres.expressions import ArraySubquery
from django.db.models import QuerySet, OuterRef, F, Func, Count, Value, CharField
from django.db.models.functions import JSONObject

from contrast_api.orm_helpers import SubqueryCount
from uncontrast_studies.models import (
    UnConExperiment,
    UnConSample,
    UnConModalityType,
    UnConStimulusCategory,
    UnConsciousnessMeasureType,
    UnConsciousnessMeasurePhase,
    UnConTaskType,
    UnConProcessingMainDomain,
    UnConSuppressedStimulus,
    UnConSuppressionMethodType,
    UnConMainParadigm,
    UnConsciousnessMeasure,
    UnConTargetStimulus,
    UnConStimulusSubCategory,
)
from uncontrast_studies.processors.base import BaseProcessor


class GrandOverviewPieGraphDataProcessor(BaseProcessor):
    def __init__(self, experiments: QuerySet[UnConExperiment], **kwargs):
        super().__init__(experiments=experiments, **kwargs)

    def process(self):
        process_func = getattr(self, "process_significance")
        return process_func()

    def process_significance(self):
        experiments_subquery_by_breakdown = self.experiments

        qs = self._aggregate_query_by_breakdown(experiments_subquery_by_breakdown)
        return qs

    def _aggregate_query_by_breakdown(self, experiments: QuerySet[UnConExperiment]):
        if self.is_csv:
            ids = experiments.values_list("id", flat=True)
            return set(list(itertools.chain.from_iterable(ids)))

        subquery = (
            experiments.values("significance")
            .distinct()
            .annotate(experiment_count=Count("id", distinct=True))
            .annotate(data=JSONObject(key=F("significance"), value=F("experiment_count")))
            .values_list("data")
        )
        """
        Discussion: Unlike most, we don't have "two" levels of grouping here 
        (e.g the series_name is the subset by paradigm, or whatever we're measuring 
        and the actual series data for each subset)
        I wanted to keep the general structure of the code the same, so I'm not using
        "aggregate" which might have been better here, but returning an array with annotate with as single item
        
        """
        qs = (
            experiments.annotate(series=ArraySubquery(subquery))
            .annotate(series_name=Value("Grand Overview", output_field=CharField()))
            .annotate(value=SubqueryCount(experiments))
            .values("series_name", "value", "series")
        )[0:1]

        # qs = (experiments
        #     .aggregate(
        #         series=ArraySubquery(subquery),
        #         series_name=Value("Grand Overview", output_field=CharField()),
        #         value=Count("id", distinct=True)
        #     )
        # )

        # Note we're filtering out empty timeseries with the cardinality option
        return qs
