from collections import namedtuple

from configuration.uncontrast_initial_data_types import (
    uncon_consciousness_measures_types,
    uncon_consciousness_measures_phases,
)
from contrast_api.data_migration_functionality.errors import InvalidConsciousnessMeasureDataError

UnConResolvedConMeasure = namedtuple(
    "UnConResolvedConMeasure",
    [
        "phase",
        "type",
        "sub_type",
        "number_of_trials",
        "number_of_awareness_participants",
        "is_cm_pax_same_as_task",
        "is_performance_above_chance",
        "is_trial_excluded_based_on_measure",
        "notes",
    ],
)


def resolve_consciousness_measures(item: dict, index: str):
    NULL_VALUES = ["", "NA", "N/A", "n/a", "missing"]
    resolved_consciousness_measures = []

    cm_main_type_data = item["Consciousness Measures Main type"]
    cm_specific_type_data = item["Consciousness Measures Specific type"]
    cm_phase_data = item["Consciousness Measures Phase"]
    number_of_trials_objective_data = item["Consciousness Measures Number of trials for the objective measure"]
    is_same_as_task_data = item[
        "Consciousness Measures Is the measure taken from the same participants as the main task?"
    ]
    number_of_awareness_participants_data = item["Consciousness Measures Number of participants of the awareness test"]
    is_above_chance_data = item["Consciousness Measures Is the performance above chance?"]
    is_trials_excluded_data = item[
        "Consciousness Measures Were trials excluded from the analysis based on the measure?"
    ]

    resolved_cm_main_type = str(cm_main_type_data).strip()
    resolved_cm_specific_type = str(cm_specific_type_data).strip()
    main_types = []
    specific_types = []

    if "+" not in resolved_cm_main_type:
        resolved_main_type = resolved_cm_main_type
        main_types.append(resolved_main_type)
    else:
        main_types = resolved_cm_main_type.split("+")
    main_types = [resolved_type.strip() for resolved_type in main_types]

    if "+" not in resolved_cm_specific_type:
        resolved_main_type = resolved_cm_specific_type
        specific_types.append(resolved_main_type)
    else:
        specific_types = resolved_cm_specific_type.split("+")
    specific_types = [resolved_type.strip() for resolved_type in specific_types]

    # TODO: change logic to include a case of multiple specific types
    for resolved_type in main_types:
        if resolved_type not in uncon_consciousness_measures_types.keys():
            raise InvalidConsciousnessMeasureDataError(
                f"invalid consciousness measure main type {resolved_type}, index {index}"
            )
        else:
            main_type = resolved_type
            if len(uncon_consciousness_measures_types[main_type]) == 0 and resolved_cm_specific_type in NULL_VALUES:
                specific_type = None
            elif len(uncon_consciousness_measures_types[main_type]) > 0 and resolved_cm_specific_type in NULL_VALUES:
                raise InvalidConsciousnessMeasureDataError(
                    f"missing CM specific type for main type {main_type}, index {index}"
                )
            elif resolved_cm_specific_type in uncon_consciousness_measures_types[main_type]:
                specific_type = resolved_cm_specific_type
            else:
                raise InvalidConsciousnessMeasureDataError(
                    f"invalid CM specific type {resolved_cm_specific_type} for main type {main_type}, index {index}"
                )

        resolved_cm_phase = str(cm_phase_data).strip()
        if resolved_cm_phase not in uncon_consciousness_measures_phases:
            raise InvalidConsciousnessMeasureDataError(
                f"invalid consciousness measure phase {resolved_cm_phase}, index {index}"
            )
        else:
            phase = resolved_cm_phase

        if number_of_trials_objective_data in NULL_VALUES:
            resolved_number_of_trials = None
        else:
            try:
                resolved_number_of_trials = int(number_of_trials_objective_data)
            except TypeError:
                raise InvalidConsciousnessMeasureDataError(
                    f"invalid numeric data for number of trials (column AD), index {index}"
                )

        if number_of_awareness_participants_data in NULL_VALUES:
            resolved_number_of_awareness_participants = None
        else:
            try:
                resolved_number_of_awareness_participants = int(number_of_awareness_participants_data)
            except TypeError:
                raise InvalidConsciousnessMeasureDataError(
                    f"invalid numeric data for number of awareness participants (column AF), index {index}"
                )

        if str(is_same_as_task_data) in NULL_VALUES:
            resolved_is_same_as_task = None
        elif str(is_same_as_task_data).strip().lower() == "yes":
            resolved_is_same_as_task = True
        elif str(is_same_as_task_data).strip().lower() == "no":
            resolved_is_same_as_task = False
        else:
            raise InvalidConsciousnessMeasureDataError(
                f"invalid boolean data for is_same_as_task (column AE), index {index}"
            )

        if str(is_above_chance_data) in NULL_VALUES:
            resolved_is_above_chance = None
        elif str(is_above_chance_data).strip().lower() == "yes":
            resolved_is_above_chance = True
        elif str(is_above_chance_data).strip().lower() == "no":
            resolved_is_above_chance = False
        else:
            raise InvalidConsciousnessMeasureDataError(
                f"invalid boolean data for is_performance_above_chance (column AG), index {index}"
            )

        if str(is_trials_excluded_data) in NULL_VALUES:
            resolved_were_trials_excluded = None
        elif str(is_trials_excluded_data).strip().lower() == "yes":
            resolved_were_trials_excluded = True
        elif str(is_trials_excluded_data).strip().lower() == "no":
            resolved_were_trials_excluded = False
        else:
            raise InvalidConsciousnessMeasureDataError(
                f"invalid boolean data for were_trials_excluded (column AH), index {index}"
            )

        resolved_consciousness_measures.append(
            UnConResolvedConMeasure(
                type=main_type,
                phase=phase,
                sub_type=specific_type,
                number_of_trials=resolved_number_of_trials,
                number_of_awareness_participants=resolved_number_of_awareness_participants,
                is_performance_above_chance=resolved_is_above_chance,
                is_trial_excluded_based_on_measure=resolved_were_trials_excluded,
                is_cm_pax_same_as_task=resolved_is_same_as_task,
                notes=None,
            )
        )
    return resolved_consciousness_measures
