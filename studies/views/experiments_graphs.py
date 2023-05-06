from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.choices import InterpretationsChoices
from studies.filters import ExperimentFilter
from studies.models import Experiment
from studies.open_api_parameters import number_of_experiments_parameter, \
    is_reporting_filter_parameter, theory_driven_filter_parameter, type_of_consciousness_filter_parameter, \
    breakdown_parameter, theory_single_required_parameter, theory_single_optional_parameter, \
    techniques_multiple_optional_parameter, paradigms_multiple_optional_parameter, \
    stimuli_categories_multiple_optional_parameter, \
    populations_multiple_optional_parameter, stimuli_modalities_multiple_optional_parameter, \
    finding_tags_types_multiple_optional_parameter, finding_tags_families_multiple_optional_parameter, \
    consciousness_measure_phases_multiple_optional_parameter, consciousness_measure_types_multiple_optional_parameter, \
    measures_multiple_optional_parameter, tasks_multiple_optional_parameter, types_multiple_optional_parameter, \
    theory_driven_multiple_optional_parameter, \
    paradigms_families_multiple_optional_parameter, techniques_multiple_optional_parameter_id_based
from studies.processors.across_the_years import AcrossTheYearsGraphDataProcessor
from studies.processors.frequencies import FrequenciesGraphDataProcessor
from studies.processors.journals import JournalsGraphDataProcessor
from studies.processors.nations_of_consciousness import NationOfConsciousnessDataProcessor
from studies.processors.parameters_distribution_bar import ParametersDistributionBarGraphDataProcessor
from studies.processors.parameters_distribution_free_queries import ParametersDistributionFreeQueriesDataProcessor
from studies.processors.parameters_distribution_pie import ParametersDistributionPieGraphDataProcessor
from studies.processors.parameters_distribution_theory_comparison_pie import \
    ComparisonParametersDistributionPieGraphDataProcessor
from studies.processors.theory_driven_distribution_pie import TheoryDrivenDistributionPieGraphDataProcessor
from studies.processors.timings import TimingsGraphDataProcessor
from studies.serializers import FullExperimentSerializer, NationOfConsciousnessGraphSerializer, \
    AcrossTheYearsGraphSerializer, BarGraphSerializer, StackedBarGraphSerializer, DurationGraphSerializer, \
    NestedPieChartSerializer, ComparisonNestedPieChartSerializer, PieChartSerializer


class ExperimentsGraphsViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = FullExperimentSerializer
    pagination_class = None
    queryset = Experiment.objects \
        .select_related("study", "study__approval_process", "study__submitter") \
        .filter(study__approval_status=ApprovalChoices.APPROVED)

    filterset_class = ExperimentFilter
    graph_serializers = {
        "nations_of_consciousness": NationOfConsciousnessGraphSerializer,
        "across_the_years": AcrossTheYearsGraphSerializer,
        "journals": BarGraphSerializer,
        "parameters_distribution_bar": StackedBarGraphSerializer,
        "timings": DurationGraphSerializer,
        "frequencies": DurationGraphSerializer,
        "parameters_distribution_pie": NestedPieChartSerializer,
        "parameters_distribution_theories_comparison": PieChartSerializer,
        "parameters_distribution_free_queries": BarGraphSerializer,
        "theory_driven_distribution_pie": NestedPieChartSerializer
    }

    graph_processors = {
        "nations_of_consciousness": NationOfConsciousnessDataProcessor,
        "across_the_years": AcrossTheYearsGraphDataProcessor,
        "journals": JournalsGraphDataProcessor,
        "parameters_distribution_bar": ParametersDistributionBarGraphDataProcessor,
        "parameters_distribution_pie": ParametersDistributionPieGraphDataProcessor,
        "parameters_distribution_theories_comparison": ComparisonParametersDistributionPieGraphDataProcessor,
        "parameters_distribution_free_queries": ParametersDistributionFreeQueriesDataProcessor,
        "frequencies": FrequenciesGraphDataProcessor,
        "timings": TimingsGraphDataProcessor,
        "theory_driven_distribution_pie": TheoryDrivenDistributionPieGraphDataProcessor,

    }

    @extend_schema(responses=NestedPieChartSerializer,
                   parameters=[
                       OpenApiParameter(name="interpretation",
                                        description="supporting or challenging",
                                        type=str,
                                        enum=[InterpretationsChoices.PRO,
                                              InterpretationsChoices.CHALLENGES],
                                        required=True),
                       number_of_experiments_parameter,
                       is_reporting_filter_parameter,
                       theory_driven_filter_parameter,
                       type_of_consciousness_filter_parameter,
                   ])
    @action(detail=False, methods=["GET"], serializer_class=NationOfConsciousnessGraphSerializer)
    def theory_driven_distribution_pie(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(responses=NationOfConsciousnessGraphSerializer(many=True),
                   parameters=[
                       OpenApiParameter(name='theory',
                                        type=str,
                                        required=False,
                                        many=True,
                                        description='theory filter - supports multiple'),
                       number_of_experiments_parameter,
                       is_reporting_filter_parameter,
                       theory_driven_filter_parameter,
                       type_of_consciousness_filter_parameter,
                   ])
    @action(detail=False, methods=["GET"], serializer_class=NationOfConsciousnessGraphSerializer)
    def nations_of_consciousness(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(responses=BarGraphSerializer(many=True),
                   parameters=[theory_single_optional_parameter,
                               number_of_experiments_parameter,
                               is_reporting_filter_parameter,
                               theory_driven_filter_parameter,
                               type_of_consciousness_filter_parameter,

                               ])
    @action(detail=False, methods=["GET"], serializer_class=BarGraphSerializer)
    def journals(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(responses=BarGraphSerializer(many=True),
                   parameters=[breakdown_parameter,
                               number_of_experiments_parameter,
                               is_reporting_filter_parameter,
                               theory_driven_filter_parameter,
                               type_of_consciousness_filter_parameter,
                               ])
    @action(detail=False, methods=["GET"], serializer_class=NestedPieChartSerializer)
    def parameters_distribution_pie(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(responses=BarGraphSerializer(many=True),
                   parameters=[breakdown_parameter,
                               number_of_experiments_parameter,
                               is_reporting_filter_parameter,
                               theory_driven_filter_parameter,
                               type_of_consciousness_filter_parameter,
                               OpenApiParameter(name="interpretation",
                                                description="supporting or challenging",
                                                type=str,
                                                enum=[InterpretationsChoices.PRO,
                                                      InterpretationsChoices.CHALLENGES],
                                                required=True)])
    @action(detail=False, methods=["GET"], serializer_class=PieChartSerializer)
    def parameters_distribution_theories_comparison(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(responses=AcrossTheYearsGraphSerializer(many=True),
                   parameters=[breakdown_parameter,
                               number_of_experiments_parameter,
                               is_reporting_filter_parameter,
                               theory_driven_filter_parameter,
                               type_of_consciousness_filter_parameter,
                               ],

                   )
    @action(detail=False, methods=["GET"], serializer_class=AcrossTheYearsGraphSerializer)
    def across_the_years(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(responses=StackedBarGraphSerializer(many=True),
                   parameters=[theory_single_required_parameter,
                               number_of_experiments_parameter,
                               breakdown_parameter,
                               is_reporting_filter_parameter,
                               theory_driven_filter_parameter,
                               type_of_consciousness_filter_parameter,
                               ])
    @action(detail=False, methods=["GET"], serializer_class=StackedBarGraphSerializer)
    def parameters_distribution_bar(self, request, *args, **kwargs):
        # TODO make theory required in swagger, change to support text and id
        # TODO , why is no info
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(responses=DurationGraphSerializer(many=True),
                   parameters=[theory_single_optional_parameter,
                               techniques_multiple_optional_parameter,
                               # number_of_experiments_parameter,
                               is_reporting_filter_parameter,
                               theory_driven_filter_parameter,
                               type_of_consciousness_filter_parameter,

                               ])
    @action(detail=False, methods=["GET"], serializer_class=DurationGraphSerializer)
    def frequencies(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(responses=DurationGraphSerializer(many=True),
                   parameters=[theory_single_optional_parameter,
                               OpenApiParameter(name='sort_first',
                                                description='sort needed for certain graphs',
                                                type=str,
                                                required=False),
                               techniques_multiple_optional_parameter,
                               OpenApiParameter(name='tags_types',
                                                description='tags_types optional for timings graphs',
                                                type=str,
                                                many=True,
                                                required=False),
                               # number_of_experiments_parameter,
                               is_reporting_filter_parameter,
                               theory_driven_filter_parameter,
                               type_of_consciousness_filter_parameter,
                               ])
    @action(detail=False, methods=["GET"], serializer_class=DurationGraphSerializer)
    def timings(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(responses=BarGraphSerializer(many=True),
                   parameters=[
                       breakdown_parameter,
                       techniques_multiple_optional_parameter_id_based,
                       paradigms_multiple_optional_parameter,
                       paradigms_families_multiple_optional_parameter,
                       stimuli_categories_multiple_optional_parameter,
                       stimuli_modalities_multiple_optional_parameter,
                       populations_multiple_optional_parameter,
                       finding_tags_types_multiple_optional_parameter,
                       finding_tags_families_multiple_optional_parameter,
                       consciousness_measure_phases_multiple_optional_parameter,
                       consciousness_measure_types_multiple_optional_parameter,
                       measures_multiple_optional_parameter,
                       tasks_multiple_optional_parameter,
                       types_multiple_optional_parameter,
                       is_reporting_filter_parameter,
                       type_of_consciousness_filter_parameter,
                       theory_driven_multiple_optional_parameter,
                       number_of_experiments_parameter,

                   ])
    @action(detail=False, methods=["GET"], serializer_class=BarGraphSerializer)
    def parameters_distribution_free_queries(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

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
