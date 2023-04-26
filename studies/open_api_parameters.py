from drf_spectacular.utils import OpenApiParameter

from studies.choices import TheoryDrivenChoices, ReportingChoices, TypeOfConsciousnessChoices

BREAKDOWN_OPTIONS = ["paradigm_family",
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
                     "measure"]

number_of_experiments_parameter = OpenApiParameter(name='min_number_of_experiments', type=int, required=False)

is_reporting_filter_parameter = OpenApiParameter(name="is_reporting", type=str, description="Optional filter",
                                                 enum=[option[0] for option in ReportingChoices.choices] + ["either"])

theory_driven_filter_parameter = OpenApiParameter(name="theory_driven", type=str, description="Optional filter",
                                                  enum=[option[0] for option in TheoryDrivenChoices.choices] + [
                                                      "either"])

type_of_consciousness_filter_parameter = OpenApiParameter(name="type_of_consciousness", type=str,
                                                          description="Optional filter",
                                                          enum=[option[0] for option in
                                                                TypeOfConsciousnessChoices.choices] + ["either"])

breakdown_parameter = OpenApiParameter(name='breakdown', description='breakdown needed for certain graphs', type=str,
                                       enum=BREAKDOWN_OPTIONS, required=True)

theory_single_required_parameter = OpenApiParameter(name='theory', type=str, required=True, description='theory filter')

theory_single_optional_parameter = OpenApiParameter(name='theory', type=str, required=False,
                                                    description='theory filter')

techniques_multiple_optional_parameter = OpenApiParameter(name='techniques',
                                                          description='techniques optional for frequencies/timings graphs',
                                                          type=str, many=True, required=False)

paradigms_multiple_optional_parameter = OpenApiParameter(name='paradigms',
                                                         description='paradigms optional for frequencies/timings graphs',
                                                         type=str, many=True, required=False)

paradigms__families_multiple_optional_parameter = OpenApiParameter(name='paradigm_families',
                                                                   description='paradigms families optional for frequencies/timings graphs',
                                                                   type=str, many=True, required=False)

stimuli_categories_multiple_optional_parameter = OpenApiParameter(name='stimuli_categories',
                                                                  description='stimuli categories families optional for frequencies/timings graphs',
                                                                  type=str, many=True, required=False)

stimuli_modalities_multiple_optional_parameter = OpenApiParameter(name='stimuli_modalities',
                                                                  description='stimuli modalities optional for frequencies/timings graphs',
                                                                  type=str, many=True, required=False)

populations_multiple_optional_parameter = OpenApiParameter(name='populations',
                                                           description='populations optional for frequencies/timings graphs',
                                                           type=str, many=True, required=False)

finding_tags_types_multiple_optional_parameter = OpenApiParameter(name='finding_tags_types',
                                                           description='finding tags types optional for frequencies/timings graphs',
                                                           type=str, many=True, required=False)

finding_tags_families_multiple_optional_parameter = OpenApiParameter(name='populatifinding_tags_familiesons',
                                                           description='finding tags families optional for frequencies/timings graphs',
                                                           type=str, many=True, required=False)