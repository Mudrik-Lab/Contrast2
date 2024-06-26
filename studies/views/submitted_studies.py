from django.db.models import Prefetch
from rest_framework import filters

from contrast_api.choices import StudyTypeChoices
from contrast_api.studies.permissions import SubmitterOnlyPermission
from studies.models import Measure, Task, FindingTag, ConsciousnessMeasure, Stimulus, Paradigm, Study
from studies.serializers import StudyWithExperimentsSerializer

from studies.views.base_submitted_studies import BaseSubmitStudiesViewSert


class SubmitStudiesViewSet(BaseSubmitStudiesViewSert):
    """
    Getting/creating studies I've submitted, editing, etc
    Also allows single link of a specific study (as result of search perhaps)
    And searching for studies by title/DOI
    """

    search_fields = ["title", "DOI"]
    filter_backends = [filters.SearchFilter]
    serializer_class = StudyWithExperimentsSerializer
    permission_classes = [SubmitterOnlyPermission]
    queryset = Study.objects.select_related("approval_process")

    def filter_and_prefetch_queryset(self, queryset):
        return queryset.filter(type=StudyTypeChoices.CONSCIOUSNESS).prefetch_related(
            "experiments",
            "authors",
            "experiments__techniques",
            "experiments__theory_driven_theories",
            "experiments__aggregated_theories",
            Prefetch("experiments__measures", queryset=Measure.objects.select_related("type")),
            Prefetch("experiments__tasks", queryset=Task.objects.select_related("type")),
            Prefetch("experiments__finding_tags", queryset=FindingTag.objects.select_related("type")),
            Prefetch(
                "experiments__consciousness_measures",
                queryset=ConsciousnessMeasure.objects.select_related("type", "phase"),
            ),
            Prefetch(
                "experiments__stimuli", queryset=Stimulus.objects.select_related("category", "sub_category", "modality")
            ),
            Prefetch("experiments__paradigms", queryset=Paradigm.objects.select_related("parent", "parent__parent")),
            "experiments__samples",
        )
