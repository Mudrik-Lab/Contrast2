from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.models import Study
from studies.serializers import ExcludedStudySerializer


class ExcludedStudiesViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = ExcludedStudySerializer

    queryset = Study.objects.select_related("approval_process").filter(
        approval_status=ApprovalChoices.REJECTED
    )  # TODO migrate this to custom manager
