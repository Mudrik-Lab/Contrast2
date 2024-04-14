from drf_spectacular.utils import OpenApiParameter

from contrast_api.choices import (
    TheoryDrivenChoices,
    ReportingChoices,
    TypeOfConsciousnessChoices,
    InterpretationsChoices,
)

BREAKDOWN_OPTIONS = [
    "paradigm",
    "population",
    "task",
    "suppressed_stimuli_category",
    "suppressed_stimuli_modality",
    "target_stimuli_category",
    "target_stimuli_modality",
    "consciousness_measure_phase",
    "consciousness_measure_type",
    "is_target_same_as_suppressed_stimulus",
    "suppression_method",
    "processing_domain",
]

number_of_experiments_parameter = OpenApiParameter(name="min_number_of_experiments", type=int, required=False)


breakdown_parameter = OpenApiParameter(
    name="breakdown", description="breakdown needed for certain graphs", type=str, enum=BREAKDOWN_OPTIONS, required=True
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
