from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from uncontrast_studies.filters import UnConExperimentFilter
from uncontrast_studies.open_api_parameters import (
    number_of_experiments_parameter,
    breakdown_parameter,
    paradigms_multiple_optional_parameter,
    populations_multiple_optional_parameter,
    target_stimuli_categories_multiple_optional_parameter,
    target_stimuli_modalities_multiple_optional_parameter,
    suppressed_stimuli_categories_multiple_optional_parameter,
    suppressed_stimuli_modalities_multiple_optional_parameter,
    consciousness_measure_phases_multiple_optional_parameter,
    consciousness_measure_types_multiple_optional_parameter,
    tasks_multiple_optional_parameter,
    types_multiple_optional_parameter,
    processing_domain_multiple_optional_parameter,
    suppression_methods_multiple_optional_parameter,
    is_trial_excluded_based_on_measure_optional_parameter,
    mode_of_presentation_optional_parameter,
    outcome_types_optional_parameter,
    continuous_breakdown_options,
    bin_size_parameter,
    are_participants_excluded,
    paradigm_single_optional_parameter,
    breakdown_parameter_with_significance,
)
from contrast_api.open_api_parameters import is_csv
from uncontrast_studies.processors.distribution_of_effects_across_parameters import (
    DistributionOfEffectsAcrossParametersGraphDataProcessor,
)
from uncontrast_studies.processors.experiments_comparison import ComparisonParametersDistributionPieGraphDataProcessor
from uncontrast_studies.processors.grand_overview_pie import GrandOverviewPieGraphDataProcessor
from uncontrast_studies.processors.trends_over_time import TrendsOverYearsGraphDataProcessor
from uncontrast_studies.processors.journals import JournalsGraphDataProcessor
from uncontrast_studies.processors.nations_of_consciousness import NationOfConsciousnessDataProcessor
from uncontrast_studies.processors.parameters_distribution_bar import ParametersDistributionBarGraphDataProcessor
from uncontrast_studies.processors.parameters_distribution_free_queries import (
    ParametersDistributionFreeQueriesDataProcessor,
)
from uncontrast_studies.processors.parameters_distribution_pie import ParametersDistributionPieGraphDataProcessor


from contrast_api.serializers import (
    TrendsOverYearsGraphSerializer,
    BarGraphSerializer,
    StackedBarGraphSerializer,
    NestedPieChartSerializer,
    PieChartSerializer,
    HistogramsGraphSerializer,
)
from uncontrast_studies.serializers import NationOfConsciousnessBySignificanceGraphSerializer
from uncontrast_studies.models import UnConExperiment
from uncontrast_studies.resources.full_experiment import FullUnConExperimentResource
from uncontrast_studies.serializers import FullUnConExperimentSerializer


class UnConExperimentsGraphsViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = FullUnConExperimentSerializer
    pagination_class = None
    queryset = UnConExperiment.objects.select_related("study", "study__approval_process", "study__submitter").filter(
        study__approval_status=ApprovalChoices.APPROVED
    )

    filterset_class = UnConExperimentFilter
    graph_serializers = {
        "nations_of_consciousness": NationOfConsciousnessBySignificanceGraphSerializer,
        "trends_over_years": TrendsOverYearsGraphSerializer,
        "journals": BarGraphSerializer,
        "parameters_distribution_bar": StackedBarGraphSerializer,
        "parameters_distribution_pie": NestedPieChartSerializer,
        "parameters_distribution_free_queries": BarGraphSerializer,
        "parameters_distribution_experiments_comparison": PieChartSerializer,
        "distribution_of_effects_across_parameters": HistogramsGraphSerializer,
        "grand_overview_pie": PieChartSerializer,
    }

    graph_processors = {
        "nations_of_consciousness": NationOfConsciousnessDataProcessor,
        "trends_over_years": TrendsOverYearsGraphDataProcessor,
        "journals": JournalsGraphDataProcessor,
        "parameters_distribution_bar": ParametersDistributionBarGraphDataProcessor,
        "parameters_distribution_pie": ParametersDistributionPieGraphDataProcessor,
        "parameters_distribution_free_queries": ParametersDistributionFreeQueriesDataProcessor,
        "parameters_distribution_experiments_comparison": ComparisonParametersDistributionPieGraphDataProcessor,
        "distribution_of_effects_across_parameters": DistributionOfEffectsAcrossParametersGraphDataProcessor,
        "grand_overview_pie": GrandOverviewPieGraphDataProcessor,
    }

    @extend_schema(
        responses={200: PieChartSerializer(many=False)},
        parameters=[
            number_of_experiments_parameter,
            paradigms_multiple_optional_parameter,
            suppressed_stimuli_categories_multiple_optional_parameter,
            suppressed_stimuli_modalities_multiple_optional_parameter,
            target_stimuli_categories_multiple_optional_parameter,
            target_stimuli_modalities_multiple_optional_parameter,
            processing_domain_multiple_optional_parameter,
            suppression_methods_multiple_optional_parameter,
            populations_multiple_optional_parameter,
            consciousness_measure_phases_multiple_optional_parameter,
            consciousness_measure_types_multiple_optional_parameter,
            tasks_multiple_optional_parameter,
            types_multiple_optional_parameter,
            # is_target_same_as_suppressed_stimulus_optional_parameter,
            # is_cm_same_participants_as_task_optional_parameter,
            is_trial_excluded_based_on_measure_optional_parameter,
            mode_of_presentation_optional_parameter,
            outcome_types_optional_parameter,
            are_participants_excluded,
            is_csv,
        ],
    )
    @action(detail=False, methods=["GET"], serializer_class=PieChartSerializer)
    def grand_overview_pie(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, many=False, *args, **kwargs)

    @extend_schema(
        responses=NationOfConsciousnessBySignificanceGraphSerializer(many=True),
        parameters=[number_of_experiments_parameter, is_csv, paradigm_single_optional_parameter],
    )
    @action(detail=False, methods=["GET"], serializer_class=NationOfConsciousnessBySignificanceGraphSerializer)
    def nations_of_consciousness(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(
        responses=BarGraphSerializer(many=True),
        parameters=[
            number_of_experiments_parameter,
            is_csv,
        ],
    )
    @action(detail=False, methods=["GET"], serializer_class=BarGraphSerializer)
    def journals(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(
        responses=NestedPieChartSerializer(many=False),
        parameters=[
            breakdown_parameter,
            number_of_experiments_parameter,
            is_csv,
        ],
    )
    @action(detail=False, methods=["GET"], serializer_class=NestedPieChartSerializer)
    def parameters_distribution_pie(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(
        responses=TrendsOverYearsGraphSerializer(many=True),
        parameters=[
            breakdown_parameter_with_significance,
            is_csv,
            number_of_experiments_parameter,
        ],
    )
    @action(detail=False, methods=["GET"], serializer_class=TrendsOverYearsGraphSerializer)
    def trends_over_years(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(
        responses=PieChartSerializer(many=True),
        parameters=[
            breakdown_parameter,
            number_of_experiments_parameter,
            is_csv,
        ],
    )
    @action(detail=False, methods=["GET"], serializer_class=PieChartSerializer)
    def parameters_distribution_experiments_comparison(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(
        responses=BarGraphSerializer(many=True),
        parameters=[
            breakdown_parameter,
            paradigms_multiple_optional_parameter,
            suppressed_stimuli_categories_multiple_optional_parameter,
            suppressed_stimuli_modalities_multiple_optional_parameter,
            target_stimuli_categories_multiple_optional_parameter,
            target_stimuli_modalities_multiple_optional_parameter,
            processing_domain_multiple_optional_parameter,
            suppression_methods_multiple_optional_parameter,
            populations_multiple_optional_parameter,
            consciousness_measure_phases_multiple_optional_parameter,
            consciousness_measure_types_multiple_optional_parameter,
            tasks_multiple_optional_parameter,
            types_multiple_optional_parameter,
            # is_target_same_as_suppressed_stimulus_optional_parameter,
            # is_cm_same_participants_as_task_optional_parameter,
            is_trial_excluded_based_on_measure_optional_parameter,
            mode_of_presentation_optional_parameter,
            outcome_types_optional_parameter,
            are_participants_excluded,
            number_of_experiments_parameter,
            is_csv,
        ],
    )
    @action(detail=False, methods=["GET"], serializer_class=BarGraphSerializer)
    def parameters_distribution_free_queries(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(
        responses=StackedBarGraphSerializer(many=True),
        parameters=[
            number_of_experiments_parameter,
            breakdown_parameter,
            is_csv,
        ],
    )
    @action(detail=False, methods=["GET"], serializer_class=StackedBarGraphSerializer)
    def parameters_distribution_bar(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    @extend_schema(
        responses=HistogramsGraphSerializer(many=True),
        parameters=[
            continuous_breakdown_options,
            number_of_experiments_parameter,
            bin_size_parameter,
            is_csv,
        ],
    )
    @action(detail=False, methods=["GET"], serializer_class=HistogramsGraphSerializer)
    def distribution_of_effects_across_parameters(self, request, *args, **kwargs):
        return self.graph(request, graph_type=self.action, *args, **kwargs)

    def get_serializer_by_graph_type(self, graph_type, data, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.graph_serializers.get(graph_type)
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(instance=data, *args, **kwargs)

    def graph(self, request, graph_type, many=True, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        graph_data_processor = self.graph_processors.get(graph_type)
        if graph_data_processor is None:
            raise GraphProcessNotRegisteredException(graph_type)

        graph_processor = graph_data_processor(queryset, **request.query_params)
        graph_data = graph_processor.process()
        if not graph_processor.is_csv:
            serializer = self.get_serializer_by_graph_type(graph_type, data=graph_data, many=many)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            """
            we manipulate the data for csv inside the processor to return a flattened list, 
            Here we select from Experiment with all relevant prefetching and select_related for relations
            And pass it through the import-export custom resource we've defined
            """
            flattened_ids = graph_data
            dataset = FullUnConExperimentResource().export(
                queryset=UnConExperiment.objects.related().filter(id__in=flattened_ids)
            )
            response = HttpResponse(
                dataset.csv,
                content_type="text/csv",
                headers={"Content-Disposition": 'attachment; filename="export.csv"'},
            )

            return response


class GraphProcessNotRegisteredException(Exception):
    pass
