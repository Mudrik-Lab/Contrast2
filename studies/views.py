from django.shortcuts import render
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.graph_data_processors import NationOfConsciousnessDataProcessor
from studies.models import Study, Experiment
from studies.serializers import StudySerializer, ExperimentSerializer, ExcludedStudySerializer, \
    NationOfConsciousnessGraphSerializer


# Create your views here.

class ApprovedStudiesViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = StudySerializer

    # TODO: handle creation
    queryset = Study.objects.select_related("approval_process").filter(
        approval_status=ApprovalChoices.APPROVED)  # TODO migrate this to custom manager


class ExperimentsViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = ExperimentSerializer
    # TODO: handle creation
    queryset = Experiment.objects.select_related("study").filter(study__approval_status=ApprovalChoices.APPROVED)
    graph_serializers = {
        "nations_of_consciousness": NationOfConsciousnessGraphSerializer
    }

    graph_processors = {
        "nations_of_consciousness": NationOfConsciousnessDataProcessor
    }

    def list(self, request, *args, **kwargs):
        if request.query_params.get("graph_type"):
            return self.graph(request, graph_type=request.query_params.get("graph_type"), *args, **kwargs)

        return super().list(request=request, *args, **kwargs)

    def get_serializer_by_graph_type(self, graph_type, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.graph_serializers.get(graph_type)
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def graph(self, request, graph_type, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        graph_data_processor = self.graph_processors.get(graph_type)

        graph_data = graph_data_processor(queryset).process()
        serializer = self.get_serializer_by_graph_type(graph_type, graph_data, many=True)

        return Response(serializer.data)


class ExcludedStudiesViewSet(mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = ExcludedStudySerializer

    queryset = Study.objects.select_related("approval_process").filter(
        approval_status=ApprovalChoices.REJECTED)  # TODO migrate this to custom manager
