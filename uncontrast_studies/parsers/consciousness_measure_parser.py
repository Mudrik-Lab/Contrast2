from collections import namedtuple

from configuration.uncontrast_initial_data_types import (
    uncon_consciousness_measures_types,
    uncon_consciousness_measures_phases,
)
from contrast_api.data_migration_functionality.errors import InvalidConsciousnessMeasureDataError
from uncontrast_studies.parsers.uncon_data_parsers import clean_list_from_data

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

    cm_main_type_data = clean_list_from_data(item["Consciousness Measures Main type"])
    cm_specific_type_data = clean_list_from_data(item["Consciousness Measures Specific type"])
    cm_phase_data = clean_list_from_data(item["Consciousness Measures Phase"])
    number_of_trials_objective_data = item["Consciousness Measures Number of trials for the objective measure"]
    is_same_as_task_data = item[
        "Consciousness Measures Is the measure taken from the same participants as the main task?"
    ]
    number_of_awareness_participants_data = item["Consciousness Measures Number of participants of the awareness test"]
    is_above_chance_data = item["Consciousness Measures Is the performance above chance?"]
    is_trials_excluded_data = item[
        "Consciousness Measures Were trials excluded from the analysis based on the measure?"
    ]

    if number_of_trials_objective_data in NULL_VALUES:
        resolved_number_of_trials = None
    else:
        try:
            resolved_number_of_trials = int(number_of_trials_objective_data)
        except TypeError:
            raise InvalidConsciousnessMeasureDataError(
                f"invalid numeric data for number of trials (column AD), index {index}"
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

    if number_of_awareness_participants_data in NULL_VALUES:
        resolved_number_of_awareness_participants = None
    else:
        try:
            resolved_number_of_awareness_participants = int(number_of_awareness_participants_data)
        except TypeError:
            raise InvalidConsciousnessMeasureDataError(
                f"invalid numeric data for number of awareness participants (column AF), index {index}"
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
    # resolving the non-duplicated data
    if len(cm_main_type_data) == len(cm_specific_type_data) == len(cm_phase_data):
        for idx in range(len(cm_main_type_data)):
            indexed_main_type = cm_main_type_data[idx]
            indexed_specific_type = cm_specific_type_data[idx]
            indexed_phase = cm_phase_data[idx]

            if indexed_main_type not in uncon_consciousness_measures_types.keys():
                raise InvalidConsciousnessMeasureDataError(
                    f"invalid consciousness measure main type {indexed_main_type}, index {index}"
                )
            else:
                main_type = indexed_main_type
                if len(uncon_consciousness_measures_types[main_type]) == 0 and indexed_specific_type in NULL_VALUES:
                    specific_type = None
                elif len(uncon_consciousness_measures_types[main_type]) > 0 and indexed_specific_type in NULL_VALUES:
                    raise InvalidConsciousnessMeasureDataError(
                        f"missing CM specific type for main type {main_type}, index {index}"
                    )
                elif indexed_specific_type in uncon_consciousness_measures_types[main_type]:
                    specific_type = indexed_specific_type
                else:
                    raise InvalidConsciousnessMeasureDataError(
                        f"invalid CM specific type {indexed_specific_type} for main type {main_type}, index {index}"
                    )

            if indexed_phase not in uncon_consciousness_measures_phases:
                raise InvalidConsciousnessMeasureDataError(
                    f"invalid consciousness measure phase {indexed_phase}, index {index}"
                )
            else:
                phase = indexed_phase

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
