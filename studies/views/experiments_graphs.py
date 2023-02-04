from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.filters import ExperimentFilter
from studies.models import Experiment
from studies.processors.across_the_years import AcrossTheYearsGraphDataProcessor
from studies.processors.frequencies import FrequenciesGraphDataProcessor
from studies.processors.journals import JournalsGraphDataProcessor
from studies.processors.nations_of_consciousness import NationOfConsciousnessDataProcessor
from studies.processors.parameters_distribution_bar import ParametersDistributionBarGraphDataProcessor
from studies.processors.timings import TimingsGraphDataProcessor
from studies.serializers import ExperimentSerializer, NationOfConsciousnessGraphSerializer, \
    AcrossTheYearsGraphSerializer, BarGraphSerializer, StackedBarGraphSerializer


class ExperimentsGraphsViewSet(mixins.ListModelMixin,
                               GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = ExperimentSerializer
    # TODO: handle creation
    queryset = Experiment.objects \
        .select_related("study", "study__approval_process", "study__submitter") \
        .filter(study__approval_status=ApprovalChoices.APPROVED)

    filterset_class = ExperimentFilter
    graph_serializers = {
        "nations_of_consciousness": NationOfConsciousnessGraphSerializer,
        "across_the_years": AcrossTheYearsGraphSerializer,
        "journals": BarGraphSerializer,
        "parameters_distribution_bar": StackedBarGraphSerializer
    }

    graph_processors = {
        "nations_of_consciousness": NationOfConsciousnessDataProcessor,
        "across_the_years": AcrossTheYearsGraphDataProcessor,
        "journals": JournalsGraphDataProcessor,
        "parameters_distribution_bar": ParametersDistributionBarGraphDataProcessor,
        "frequencies": FrequenciesGraphDataProcessor,
        "timings": TimingsGraphDataProcessor,

    }

    @extend_schema(parameters=[OpenApiParameter(name='graph_type',
                                                description='Graph type',
                                                type=str,
                                                enum=["nations_of_consciousness",
                                                      "across_the_years",
                                                      "journals",
                                                      "parameters_distribution_bar",
                                                      "frequencies",
                                                      "timings"
                                                      ],
                                                required=True),
                               OpenApiParameter(name='theory',
                                                type=str,
                                                required=False, #TODO add supported enum
                                                description='theory filter needed for certain graphs'),
                               OpenApiParameter(name='breakdown',
                                                description='breakdown needed for certain graphs',
                                                type=str,
                                                enum=["paradigm_family",
                                                      "paradigm",
                                                      "population",
                                                      "finding_tag",
                                                      "finding_tag_family",
                                                      "reporting",
                                                      "theory_driven",
                                                      "task",
                                                      "stimuli_category",
                                                      "modality",
                                                      "consciousness_measure_phase",
                                                      "consciousness_measure_type",
                                                      "type_of_consciousness",
                                                      "technique",
                                                      "measure"],
                                                required=False)])
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


class GraphProcessNotRegisteredException(Exception):
    pass
