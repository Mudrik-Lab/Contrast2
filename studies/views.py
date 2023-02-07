from django.shortcuts import render
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.filters import ExperimentFilter
from studies.processors.frequencies import FrequenciesGraphDataProcessor
from studies.processors.journals import JournalsGraphDataProcessor
from studies.processors.nations_of_consciousness import NationOfConsciousnessDataProcessor
from studies.processors.across_the_years import AcrossTheYearsGraphDataProcessor
from studies.models import Study, Experiment
from studies.processors.parameters_distribution_bar import ParametersDistributionBarGraphDataProcessor
from studies.processors.timings import TimingsGraphDataProcessor
from studies.serializers import StudySerializer, ExperimentSerializer, ExcludedStudySerializer, \
    NationOfConsciousnessGraphSerializer, AcrossTheYearsGraphSerializer, BarGraphSerializer, StackedBarGraphSerializer


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


class GraphProcessNotRegisteredException(Exception):
    pass


class ExperimentsViewSet(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = ExperimentSerializer
    # TODO: handle creation
    queryset = Experiment.objects.select_related("study").filter(study__approval_status=ApprovalChoices.APPROVED)
    filterset_class = ExperimentFilter
    graph_serializers = {
        "nations_of_consciousness": NationOfConsciousnessGraphSerializer,
        "across_the_years": AcrossTheYearsGraphSerializer,
        "journals": BarGraphSerializer,
        "parameters_distribution_bar":StackedBarGraphSerializer
    }

    graph_processors = {
        "nations_of_consciousness": NationOfConsciousnessDataProcessor,
        "across_the_years": AcrossTheYearsGraphDataProcessor,
        "journals": JournalsGraphDataProcessor,
        "parameters_distribution_bar": ParametersDistributionBarGraphDataProcessor,
        "frequencies": FrequenciesGraphDataProcessor,
        "timings": TimingsGraphDataProcessor,

    }

    def list(self, request, *args, **kwargs):
        if request.query_params.get("graph_type"):
            return self.graph(request, graph_type=request.query_params.get("graph_type"), *args, **kwargs)

        return super().list(request=request, *args, **kwargs)

    def get_serializer_by_graph_type(self, graph_type, data, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.graph_serializers.get(graph_type)
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(instance=data, *args, **kwargs)

    def graph(self, request, graph_type, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        graph_data_processor = self.graph_processors.get(graph_type)
        if graph_data_processor is None:
            raise GraphProcessNotRegisteredException(graph_type)

        graph_data = graph_data_processor(queryset, **request.query_params).process()
        serializer = self.get_serializer_by_graph_type(graph_type, data=graph_data, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ExcludedStudiesViewSet(mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = ExcludedStudySerializer

    queryset = Study.objects.select_related("approval_process").filter(
        approval_status=ApprovalChoices.REJECTED)  # TODO migrate this to custom manager
