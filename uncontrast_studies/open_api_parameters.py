from drf_spectacular.utils import OpenApiParameter


UNCONTRAST_GRAPH_BREAKDOWN_OPTIONS = [
    "paradigm",
    "population",
    "task",
    "suppressed_stimuli_category",
    "suppressed_stimuli_sub_category",
    "suppressed_stimuli_modality",
    "target_stimuli_category",
    "target_stimuli_sub_category",
    "target_stimuli_modality",
    "consciousness_measure_phase",
    "consciousness_measure_type",
    "is_target_same_as_suppressed_stimulus",
    "is_cm_same_participants_as_task",
    "is_trial_excluded_based_on_measure",
    "is_performance_above_chance",
    "modes_of_presentation",
    "suppression_method",
    "processing_domain",
]

UNCONTRAST_GRAPH_CONTINUOUS_BREAKDOWN_OPTIONS = [
    "suppressed_stimuli_duration",
    "number_of_stimuli",  # backwards compatibility points to suppressed
    "number_of_suppressed_stimuli",
    "number_of_target_stimuli",
    "unconsciousness_measure_number_of_trials",
    "outcome_number_of_trials",
    "unconsciousness_measure_number_of_participants_in_awareness_test",
    "sample_size_included",
    "sample_size_excluded",
    "year_of_publication",
]

number_of_experiments_parameter = OpenApiParameter(name="min_number_of_experiments", type=int, required=False)
bin_size_parameter = OpenApiParameter(name="bin_size", type=int, required=False)

continuous_breakdown_options = OpenApiParameter(
    name="continuous_breakdown",
    description="continuous breakdown needed for histograms",
    type=str,
    enum=UNCONTRAST_GRAPH_CONTINUOUS_BREAKDOWN_OPTIONS,
    required=True,
)

breakdown_parameter = OpenApiParameter(
    name="breakdown",
    description="breakdown needed for certain graphs",
    type=str,
    enum=UNCONTRAST_GRAPH_BREAKDOWN_OPTIONS,
    required=True,
)

paradigms_multiple_optional_parameter = OpenApiParameter(
    name="paradigms", description="paradigms optional", type=int, many=True, required=False
)

suppressed_stimuli_categories_multiple_optional_parameter = OpenApiParameter(
    name="suppressed_stimuli_categories",
    description="suppressed stimuli categories families",
    type=int,
    many=True,
    required=False,
)

suppressed_stimuli_modalities_multiple_optional_parameter = OpenApiParameter(
    name="suppressed_stimuli_modalities",
    description="suppressed stimuli modalities optional",
    type=int,
    many=True,
    required=False,
)

target_stimuli_categories_multiple_optional_parameter = OpenApiParameter(
    name="target_stimuli_categories",
    description="target stimuli categories families",
    type=int,
    many=True,
    required=False,
)

target_stimuli_modalities_multiple_optional_parameter = OpenApiParameter(
    name="target_stimuli_modalities",
    description="target stimuli modalities optional",
    type=int,
    many=True,
    required=False,
)


populations_multiple_optional_parameter = OpenApiParameter(
    name="populations", description="populations optional for", type=str, many=True, required=False
)

processing_domain_multiple_optional_parameter = OpenApiParameter(
    name="processing_domain_types", description="processing domains optional for", type=str, many=True, required=False
)
suppression_methods_multiple_optional_parameter = OpenApiParameter(
    name="suppression_methods_types",
    description="suppression methods optional for",
    type=str,
    many=True,
    required=False,
)


consciousness_measure_phases_multiple_optional_parameter = OpenApiParameter(
    name="consciousness_measure_phases",
    description="consciousness measure phases optional",
    type=int,
    many=True,
    required=False,
)

consciousness_measure_types_multiple_optional_parameter = OpenApiParameter(
    name="consciousness_measure_types",
    description="consciousness measure types optional",
    type=int,
    many=True,
    required=False,
)


tasks_multiple_optional_parameter = OpenApiParameter(
    name="tasks", description="tasks optional", type=int, many=True, required=False
)

types_multiple_optional_parameter = OpenApiParameter(
    name="types", description="types optional", type=str, many=True, required=False
)

is_target_same_as_suppressed_stimulus_optional_parameter = OpenApiParameter(
    name="is_target_same_as_suppressed_stimulus", type=bool, required=False, many=False
)

is_cm_same_participants_as_task_optional_parameter = OpenApiParameter(
    name="is_cm_same_participants_as_task", type=bool, required=False, many=False
)

is_trial_excluded_based_on_measure_optional_parameter = OpenApiParameter(
    name="is_trial_excluded_based_on_measure", type=bool, required=False, many=False
)
mode_of_presentation_optional_parameter = OpenApiParameter(
    name="modes_of_presentation", description="modes of presentation optional for", type=str, many=True, required=False
)
outcome_types_optional_parameter = OpenApiParameter(
    name="outcome_types", description="outcome types optional for", type=str, required=False, many=True
)

are_participants_excluded = OpenApiParameter(name="are_participants_excluded", type=bool, required=False, many=False)
