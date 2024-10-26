from collections import namedtuple

from configuration.uncontrast_initial_data_types import (
    uncon_consciousness_measures_types,
    uncon_consciousness_measures_phases,
    NULL_VALUES,
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


def resolve_numeric_value(numeric_value, index: str):
    if numeric_value in NULL_VALUES:
        resolved_numeric_value = None
    else:
        try:
            resolved_numeric_value = int(numeric_value)
        except (TypeError, ValueError):
            raise InvalidConsciousnessMeasureDataError(f"invalid numeric data [{numeric_value}], index {index}")
    return resolved_numeric_value


def resolve_boolean_value(value: str, index: str):
    if str(value).strip().lower() == "yes":
        resolved_boolean_value = True
    elif str(value).strip().lower() == "no":
        resolved_boolean_value = False
    else:
        raise InvalidConsciousnessMeasureDataError(f"invalid boolean data [{value}], index {index}")
    return resolved_boolean_value


def check_main_type(value: str, index: str):
    if value not in uncon_consciousness_measures_types.keys():
        raise InvalidConsciousnessMeasureDataError(f"invalid consciousness measure main type {value}, index {index}")
    else:
        resolved_main_type = value
    return resolved_main_type


def check_specific_type(value: str, resolved_main_type: str, index: str):
    if uncon_consciousness_measures_types[resolved_main_type] == [] and (value == "" or value == "None"):
        resolved_specific_type = None
    elif value in uncon_consciousness_measures_types[resolved_main_type]:
        resolved_specific_type = value
    else:
        raise InvalidConsciousnessMeasureDataError(
            f"missing or invalid CM specific type {value} for main type {resolved_main_type}, index {index}"
        )
    return resolved_specific_type


def check_phase(value: str, index: str):
    if value not in uncon_consciousness_measures_phases:
        raise InvalidConsciousnessMeasureDataError(f"invalid consciousness measure phase {value}, index {index}")
    else:
        resolved_phase = value
    return resolved_phase


def resolve_consciousness_measures(item: dict, index: str):
    resolved_consciousness_measures = []

    cm_main_type_data = clean_list_from_data(item["Consciousness Measures Main type"])
    cm_specific_type_data = clean_list_from_data(item["Consciousness Measures Specific type"])
    cm_phase_data = clean_list_from_data(item["Consciousness Measures Phase"])
    number_of_trials_objective_data = clean_list_from_data(
        item["Consciousness Measures Number of trials for the objective measure"], integer=True
    )
    is_same_as_task_data = clean_list_from_data(
        item["Consciousness Measures Is the measure taken from the same participants as the main task?"]
    )
    number_of_awareness_participants_data = clean_list_from_data(
        item["Consciousness Measures Number of participants of the awareness test"], integer=True
    )
    is_above_chance_data = clean_list_from_data(item["Consciousness Measures Is the performance above chance?"])
    is_trials_excluded_data = clean_list_from_data(
        item["Consciousness Measures Were trials excluded from the analysis based on the measure?"]
    )

    is_singular_main_type = len(cm_main_type_data) == 1 and not cm_main_type_data == [""]
    is_singular_specific_type = len(cm_specific_type_data) == 1
    is_singular_phase = len(cm_phase_data) == 1 and not cm_phase_data == [""]
    is_singular_number_of_trials = len(number_of_trials_objective_data) == 1
    is_singular_number_of_participants = len(number_of_awareness_participants_data) == 1
    is_singular_is_same_as_task = len(is_same_as_task_data) == 1 and not is_same_as_task_data == [""]
    is_singular_is_above_chance = len(is_above_chance_data) == 1
    is_singular_is_trials_excluded = len(is_trials_excluded_data) == 1 and not is_trials_excluded_data == [""]

    is_multiple_main_type = len(cm_main_type_data) > 1
    is_multiple_specific_type = len(cm_specific_type_data) > 1
    is_multiple_phase = len(cm_phase_data) > 1
    is_multiple_number_of_trials = len(number_of_trials_objective_data) > 1
    is_multiple_number_of_participants = len(number_of_awareness_participants_data) > 1
    is_multiple_is_same_as_task = len(is_same_as_task_data) > 1
    is_multiple_is_above_chance = len(is_above_chance_data) > 1  # noqa: F841
    is_multiple_is_trials_excluded = len(is_trials_excluded_data) > 1

    is_singular_data = (
        is_singular_main_type
        and is_singular_specific_type
        and is_singular_phase
        and is_singular_number_of_trials
        and is_singular_number_of_participants
        and is_singular_is_same_as_task
        and is_singular_is_above_chance
        and is_singular_is_trials_excluded
    )
    is_multiple_data = (
        is_multiple_main_type and is_multiple_specific_type and is_multiple_phase and is_multiple_is_same_as_task
    )

    if is_singular_data:
        resolved_main_type = check_main_type(cm_main_type_data[0], index=index)
        resolved_specific_type = check_specific_type(cm_specific_type_data[0], resolved_main_type, index=index)
        resolved_phase = check_phase(cm_phase_data[0], index=index)
        resolved_number_of_awareness_participants = resolve_numeric_value(
            number_of_awareness_participants_data[0], index=index
        )
        resolved_is_trials_excluded = resolve_boolean_value(is_trials_excluded_data[0], index=index)
        resolved_is_same_as_task = resolve_boolean_value(is_same_as_task_data[0], index=index)

        if resolved_main_type == "Objective":
            resolved_number_of_trials = resolve_numeric_value(number_of_trials_objective_data[0], index=index)
            resolved_is_above_chance = resolve_boolean_value(is_above_chance_data[0], index=index)

            resolved_consciousness_measures.append(
                UnConResolvedConMeasure(
                    type=resolved_main_type,
                    phase=resolved_phase,
                    sub_type=resolved_specific_type,
                    number_of_trials=resolved_number_of_trials,
                    number_of_awareness_participants=resolved_number_of_awareness_participants,
                    is_performance_above_chance=resolved_is_above_chance,
                    is_trial_excluded_based_on_measure=resolved_is_trials_excluded,
                    is_cm_pax_same_as_task=resolved_is_same_as_task,
                    notes=None,
                )
            )
        else:
            resolved_consciousness_measures.append(
                UnConResolvedConMeasure(
                    type=resolved_main_type,
                    phase=resolved_phase,
                    sub_type=resolved_specific_type,
                    number_of_trials=None,
                    number_of_awareness_participants=resolved_number_of_awareness_participants,
                    is_performance_above_chance=None,
                    is_trial_excluded_based_on_measure=resolved_is_trials_excluded,
                    is_cm_pax_same_as_task=resolved_is_same_as_task,
                    notes=None,
                )
            )

    elif is_multiple_data:
        objective_main_type = [(count, item) for count, item in enumerate(cm_main_type_data) if item == "Objective"]
        indices_of_objective_cm_types = [item[0] for item in objective_main_type]

        for idx in range(len(cm_main_type_data)):
            resolved_main_type = check_main_type(cm_main_type_data[idx], index=index)
            resolved_specific_type = check_specific_type(cm_specific_type_data[idx], resolved_main_type, index=index)
            resolved_phase = check_phase(cm_phase_data[idx], index=index)
            resolved_is_same_as_task = resolve_boolean_value(is_same_as_task_data[idx], index=index)

            if is_multiple_number_of_participants:
                resolved_number_of_awareness_participants = resolve_numeric_value(
                    number_of_awareness_participants_data[idx], index=index
                )
            else:
                resolved_number_of_awareness_participants = resolve_numeric_value(
                    number_of_awareness_participants_data[0], index=index
                )
            if is_multiple_is_trials_excluded:
                resolved_is_trials_excluded = resolve_boolean_value(is_trials_excluded_data[idx], index=index)
            else:
                resolved_is_trials_excluded = resolve_boolean_value(is_trials_excluded_data[0], index=index)

            if resolved_main_type == "Objective":
                objective_index = indices_of_objective_cm_types.index(idx)

                if is_multiple_number_of_trials:
                    resolved_number_of_trials = resolve_numeric_value(
                        number_of_trials_objective_data[objective_index], index=index
                    )
                else:
                    resolved_number_of_trials = resolve_numeric_value(number_of_trials_objective_data[0], index=index)
                resolved_is_above_chance = resolve_boolean_value(is_above_chance_data[objective_index], index=index)
                resolved_consciousness_measures.append(
                    UnConResolvedConMeasure(
                        type=resolved_main_type,
                        phase=resolved_phase,
                        sub_type=resolved_specific_type,
                        number_of_trials=resolved_number_of_trials,
                        number_of_awareness_participants=resolved_number_of_awareness_participants,
                        is_performance_above_chance=resolved_is_above_chance,
                        is_trial_excluded_based_on_measure=resolved_is_trials_excluded,
                        is_cm_pax_same_as_task=resolved_is_same_as_task,
                        notes=None,
                    )
                )
            else:
                resolved_consciousness_measures.append(
                    UnConResolvedConMeasure(
                        type=resolved_main_type,
                        phase=resolved_phase,
                        sub_type=resolved_specific_type,
                        number_of_trials=None,
                        number_of_awareness_participants=resolved_number_of_awareness_participants,
                        is_performance_above_chance=None,
                        is_trial_excluded_based_on_measure=resolved_is_trials_excluded,
                        is_cm_pax_same_as_task=resolved_is_same_as_task,
                        notes=None,
                    )
                )

    else:
        raise InvalidConsciousnessMeasureDataError()

    return resolved_consciousness_measures
