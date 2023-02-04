from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.models import Study
from studies.serializers import StudyWithExperimentsSerializer


class SubmitStudiesViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           GenericViewSet):
    """
    Getting/creating studies I'm submitting, adding experiments, editing, etc
    """
    queryset = Study.objects.select_related("approval_process") \
        .prefetch_related("experiments",
                          "authors",
                          "experiments__stimuli",
                          "experiments__samples",
                          "experiments__tasks",
                          "experiments__tasks",
                          "experiments__consciousness_measures",
                          "experiments__consciousness_measures__phase",
                          "experiments__consciousness_measures__type",
                          "experiments__finding_tags",
                          "experiments__finding_tags__family",
                          "experiments__finding_tags__type",
                          "experiments__finding_tags__technique"
                          ) \
        .filter(approval_status=ApprovalChoices.PENDING)
    permission_classes = [IsAuthenticated]
    serializer_class = StudyWithExperimentsSerializer

    def get_queryset(self):
        super().get_queryset() \
            .filter(ubmitter=self.request.user)
