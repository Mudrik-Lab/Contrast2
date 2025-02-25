from drf_spectacular.utils import OpenApiParameter

from contrast_api.choices import (
    TheoryDrivenChoices,
    ReportingChoices,
    TypeOfConsciousnessChoices,
    InterpretationsChoices,
    AggregatedOptionalInterpretationsChoices,
)

BREAKDOWN_OPTIONS = [
    "paradigm_family",
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
    "measure",
]

THEORY_ADDED_BREAKDOWN_OPTIONS = BREAKDOWN_OPTIONS + ["theory"]

number_of_experiments_parameter = OpenApiParameter(name="min_number_of_experiments", type=int, required=False)

is_reporting_filter_parameter = OpenApiParameter(
    name="is_reporting",
    type=str,
    description="Optional filter",
    enum=[option[0] for option in ReportingChoices.choices] + ["either"],
)

theory_driven_filter_parameter = OpenApiParameter(
    name="theory_driven",
    type=str,
    description="Optional filter",
    enum=[option[0] for option in TheoryDrivenChoices.choices] + ["either"],
)

type_of_consciousness_filter_parameter = OpenApiParameter(
    name="type_of_consciousness",
    type=str,
    description="Optional type of consciousness filter",
    enum=[option[0] for option in TypeOfConsciousnessChoices.choices] + ["either"],
)

breakdown_parameter = OpenApiParameter(
    name="breakdown", description="breakdown needed for certain graphs", type=str, enum=BREAKDOWN_OPTIONS, required=True
)

theory_added_breakdown_parameter = OpenApiParameter(
    name="breakdown",
    description="breakdown needed + theory. for certain graphs",
    type=str,
    enum=THEORY_ADDED_BREAKDOWN_OPTIONS,
    required=True,
)

theory_single_required_parameter = OpenApiParameter(name="theory", type=str, required=True, description="theory filter")

theory_single_optional_parameter = OpenApiParameter(
    name="theory", type=str, required=False, description="theory filter"
)

techniques_multiple_optional_parameter = OpenApiParameter(
    name="techniques",
    description="techniques optional for frequencies/timings graphs",
    type=str,
    many=True,
    required=False,
)

techniques_multiple_optional_parameter_id_based = OpenApiParameter(
    name="techniques", description="techniques optional for free queries", type=int, many=True, required=False
)

paradigms_multiple_optional_parameter = OpenApiParameter(
    name="paradigms", description="paradigms optional", type=int, many=True, required=False
)

paradigms_families_multiple_optional_parameter = OpenApiParameter(
    name="paradigm_families", description="paradigms families optional", type=int, many=True, required=False
)

stimuli_categories_multiple_optional_parameter = OpenApiParameter(
    name="stimuli_categories", description="stimuli categories families", type=int, many=True, required=False
)

stimuli_modalities_multiple_optional_parameter = OpenApiParameter(
    name="stimuli_modalities", description="stimuli modalities optional", type=int, many=True, required=False
)

populations_multiple_optional_parameter = OpenApiParameter(
    name="populations", description="populations optional for", type=str, many=True, required=False
)

finding_tags_types_multiple_optional_parameter = OpenApiParameter(
    name="finding_tags_types", description="finding tags types optional", type=int, many=True, required=False
)

finding_tags_families_multiple_optional_parameter = OpenApiParameter(
    name="finding_tags_families", description="finding tags families optional", type=int, many=True, required=False
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
measures_multiple_optional_parameter = OpenApiParameter(
    name="measures", description="measures optional", type=int, many=True, required=False
)

tasks_multiple_optional_parameter = OpenApiParameter(
    name="tasks", description="tasks optional", type=int, many=True, required=False
)

types_multiple_optional_parameter = OpenApiParameter(
    name="types", description="types optional", type=str, many=True, required=False
)
reporting_multiple_optional_parameter = OpenApiParameter(
    name="reporting", description="reporting optional", type=str, many=True, required=False
)

theory_driven_multiple_optional_parameter = OpenApiParameter(
    name="theory_driven", description="theory driven optional", type=str, many=True, required=False
)
interpretations = OpenApiParameter(
    name="interpretations_types",
    description="interpretations types optional - note must come with interpretation_theories",
    enum=[option[0] for option in InterpretationsChoices.choices],
    type=str,
    many=True,
    required=False,
)
aggregated_interpretation_parameter = OpenApiParameter(
    name="interpretation",
    description="supporting or challenging",
    type=str,
    enum=[InterpretationsChoices.PRO, InterpretationsChoices.CHALLENGES],
    required=True,
)

aggregated_interpretations_optional_filter = OpenApiParameter(
    name="aggregated_interpretation_filter",
    description="Aggregated interpretations types optional - defaults to all",
    enum=[option[0] for option in AggregatedOptionalInterpretationsChoices.choices],
    type=str,
    many=False,
    required=False,
    default=AggregatedOptionalInterpretationsChoices.EITHER,
)
interpretation_theories = OpenApiParameter(
    name="interpretation_theories",
    description="theories for interpretation optional - note must come with interpretations",
    type=int,
    many=True,
    required=False,
)
