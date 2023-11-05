from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.models import Study
from studies.serializers import StudySerializer


class ApprovedStudiesViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = StudySerializer

    # TODO: handle creation
    queryset = (
        Study.objects.select_related("approval_process")
        .prefetch_related("authors")
        .filter(approval_status=ApprovalChoices.APPROVED)
    )  # TODO migrate this to custom manager
