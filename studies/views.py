from django.shortcuts import render
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.models import Study, Experiment
from studies.serializers import StudySerializer, ExperimentSerializer


# Create your views here.

class ApprovedStudiesViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = StudySerializer

    # TODO: handle creation
    queryset = Study.objects.select_related("approval_process").filter(
        approval_status=ApprovalChoices.APPROVED)


class ExperimentsViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = ExperimentSerializer
    # TODO: handle creation
    queryset = Experiment.objects.select_related("study").filter(study__approval_status=ApprovalChoices.APPROVED)


class ExcludedStudiesViewSet(mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = StudySerializer

    queryset = Study.objects.select_related("approval_process").filter(
        approval_status=ApprovalChoices.REJECTED)
