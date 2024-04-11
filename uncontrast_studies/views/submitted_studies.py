from django.db.models import Prefetch, Q
from studies.models import Study, Measure, Task, FindingTag, ConsciousnessMeasure, Stimulus, Paradigm

from studies.views.base_submitted_studies import BaseSubmitStudiesViewSert
from uncontrast_studies.models import (
    UnConsciousnessMeasure,
    UnConSpecificParadigm,
    UnConTask,
    UnConFinding,
    UnConTargetStimulus,
    UnConSuppressedStimulus,
)


class SubmitUnContrastStudiesViewSet(BaseSubmitStudiesViewSert):
    """
    Getting/creating studies I've submitted, editing, etc
    Also allows single link of a specific study (as result of search perhaps)
    And searching for studies by title/DOI
    """

    def filter_and_prefetch_queryset(self, queryset):
        # TODO: add filter
        return queryset.prefetch_related(
            "uncon_experiments",
            "authors",
            Prefetch("uncon_experiments__tasks", queryset=UnConTask.objects.select_related("type")),
            Prefetch("uncon_experiments__findings", queryset=UnConFinding.objects.select_related("type")),
            Prefetch(
                "uncon_experiments__consciousness_measures",
                queryset=UnConsciousnessMeasure.objects.select_related("type", "sub_type", "phase"),
            ),
            Prefetch(
                "uncon_experiments__suppressed_stimuli",
                queryset=UnConSuppressedStimulus.objects.select_related("category", "sub_category", "modality"),
            ),
            Prefetch(
                "uncon_experiments__target_stimuli",
                queryset=UnConTargetStimulus.objects.select_related("category", "sub_category", "modality"),
            ),
            Prefetch(
                "uncon_experiments__paradigms",
                queryset=UnConSpecificParadigm.objects.select_related("parent", "parent__parent"),
            ),
            "uncon_experiments__samples",
        )
