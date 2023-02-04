from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.models import Experiment
from studies.serializers import ExperimentSerializer


class SubmittedStudyExperiments(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin,
                                mixins.UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ExperimentSerializer
    queryset = Experiment.objects.select_related("study", "study__approval_process", "study__submitter") \
        .filter(study__approval_status=ApprovalChoices.PENDING)

    def get_queryset(self):
        super().get_queryset() \
            .filter(study__approval_status=ApprovalChoices.PENDING) \
            .filter(study=self.kwargs.get("study_pk")) \
            .filter(study__submitter=self.request.user)
