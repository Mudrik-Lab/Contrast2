from collections import namedtuple
from typing import Optional

from configuration.uncontrast_initial_data_types import uncon_stimulus_categories, uncon_stimulus_modalities
from contrast_api.choices import PresentationModeChoices
from contrast_api.data_migration_functionality.errors import (
    MissingStimulusCategoryError,
    StimulusModalityError,
    StimulusModeOfPresentationError,
    StimulusDurationError,
    StimulusMetadataError,
    IncoherentStimuliDataError,
    MissingValueInStimuliError,
)
from uncontrast_studies.parsers.uncon_data_parsers import clean_list_from_data


def is_missing_number_of_trials(item: dict):
    stimuli_number_of_stimuli_data = item["Stimuli Number of different stimuli used in the experiment"]
    if stimuli_number_of_stimuli_data == "missing":
        return True
    else:
        return False


def is_target_duplicate(item: dict):
    stimuli_category_data = clean_list_from_data(item["Stimuli Category"])
    stimuli_sub_category_data = clean_list_from_data(item["Stimuli Sub-category"])
    stimuli_modality_data = clean_list_from_data(item["Stimuli Modality"])
    stimuli_number_of_stimuli_data = clean_list_from_data(
        item["Stimuli Number of different stimuli used in the experiment"], integer=True
    )

    stimuli_category_data_2 = clean_list_from_data(item["Stimuli Category 2"])
    stimuli_sub_category_data_2 = clean_list_from_data(item["Stimuli Sub-category 2"])
    stimuli_modality_data_2 = clean_list_from_data(item["Stimuli Modality 2"])
    stimuli_number_of_stimuli_data_2 = clean_list_from_data(
        item["Stimuli Number of different stimuli used in the experiment 2"], integer=True
    )

    if (
        stimuli_category_data == stimuli_category_data_2
        and stimuli_sub_category_data == stimuli_sub_category_data_2
        and stimuli_modality_data == stimuli_modality_data_2
        and stimuli_number_of_stimuli_data == stimuli_number_of_stimuli_data_2
    ):
        return True
    else:
        return False


def resolve_uncon_prime_stimuli(item: dict, index: str):
    resolved_stimuli = []
    stimuli_mode_of_presentation_data = str(item["Stimuli Mode of presentation"]).strip().lower()

    if stimuli_mode_of_presentation_data == "liminal":
        mode_of_presentation = PresentationModeChoices.LIMINAL
    elif stimuli_mode_of_presentation_data == "subliminal":
        mode_of_presentation = PresentationModeChoices.SUBLIMINAL
    else:
        raise StimulusModeOfPresentationError(
            f"{stimuli_mode_of_presentation_data} (index {index}) not valid for prime stimulus mode of presentation"
        )

    (
        is_multiple_categories_and_multiple_sub_categories,
        is_multiple_categories_and_singular_numerics,
        is_multiple_sub_categories_and_multiple_numerics,
        is_multiple_sub_categories_and_singular_numerics,
        is_no_sub_category,
        is_same_length,
        len_category,
        len_sub_category,
        stimuli_category_data,
        stimuli_sub_category_data,
        stimuli_duration_data,
        stimuli_soa_data,
        stimuli_modality_data,
        stimuli_number_of_stimuli_data,
        is_multiple_modalities,
        is_multiple_number_of_stimuli,
    ) = categorize_prime_stimulus_data(item)

    if is_same_length:
        for idx in range(len_category):
            stimulus_category = check_category(index, stimuli_category_data[idx])
            stimulus_sub_category = check_sub_category(index, stimulus_category, stimuli_sub_category_data[idx])
            stimulus_duration, stimulus_soa = check_numeric_values(
                index, stimuli_duration_data[idx], stimuli_soa_data[idx]
            )
            if is_multiple_modalities:
                stimulus_modality = stimuli_modality_data[idx]
            else:
                stimulus_modality = stimuli_modality_data[0]
            if is_multiple_number_of_stimuli:
                stimulus_number_of_stimuli = stimuli_number_of_stimuli_data[idx]
            else:
                stimulus_number_of_stimuli = stimuli_number_of_stimuli_data[0]

            resolved_stimuli.append(
                UnconResolvedStimulusData(
                    category=stimulus_category,
                    sub_category=stimulus_sub_category,
                    modality=stimulus_modality,
                    number_of_stimuli=stimulus_number_of_stimuli,
                    mode_of_presentation=mode_of_presentation,
                    duration=stimulus_duration,
                    soa=stimulus_soa,
                )
            )

    elif is_multiple_sub_categories_and_multiple_numerics:
        stimulus_category = check_category(index, stimuli_category_data[0])
        stimulus_modality = stimuli_modality_data[0]
        stimulus_number_of_stimuli = stimuli_number_of_stimuli_data[0]

        for idx in range(len_sub_category):
            stimulus_sub_category = check_sub_category(index, stimulus_category, stimuli_sub_category_data[idx])
            stimulus_duration, stimulus_soa = check_numeric_values(
                index, stimuli_duration_data[idx], stimuli_soa_data[idx]
            )

            resolved_stimuli.append(
                UnconResolvedStimulusData(
                    category=stimulus_category,
                    sub_category=stimulus_sub_category,
                    modality=stimulus_modality,
                    number_of_stimuli=stimulus_number_of_stimuli,
                    mode_of_presentation=mode_of_presentation,
                    duration=stimulus_duration,
                    soa=stimulus_soa,
                )
            )

    elif is_multiple_sub_categories_and_singular_numerics:
        stimulus_category = check_category(index, stimuli_category_data[0])
        stimulus_duration, stimulus_soa = check_numeric_values(index, stimuli_duration_data[0], stimuli_soa_data[0])
        stimulus_modality = stimuli_modality_data[0]
        stimulus_number_of_stimuli = stimuli_number_of_stimuli_data[0]
        for sub_category in stimuli_sub_category_data:
            stimulus_sub_category = check_sub_category(index, stimulus_category, sub_category)
            resolved_stimuli.append(
                UnconResolvedStimulusData(
                    category=stimulus_category,
                    sub_category=stimulus_sub_category,
                    modality=stimulus_modality,
                    number_of_stimuli=stimulus_number_of_stimuli,
                    mode_of_presentation=mode_of_presentation,
                    duration=stimulus_duration,
                    soa=stimulus_soa,
                )
            )

    elif is_multiple_categories_and_multiple_sub_categories:
        stimulus_duration, stimulus_soa = check_numeric_values(index, stimuli_duration_data[0], stimuli_soa_data[0])
        possible_categories_for_sub_category = []
        stimulus_modality = stimuli_modality_data[0]
        stimulus_number_of_stimuli = stimuli_number_of_stimuli_data[0]
        for category in stimuli_category_data:
            stimulus_category = check_category(index, category)
            possible_categories_for_sub_category.append(stimulus_category)

        for sub_category in stimuli_sub_category_data:
            is_match = False
            for stimulus_category in possible_categories_for_sub_category:
                if sub_category in uncon_stimulus_categories[stimulus_category]:
                    stimulus_sub_category = sub_category
                    resolved_stimuli.append(
                        UnconResolvedStimulusData(
                            category=stimulus_category,
                            sub_category=stimulus_sub_category,
                            modality=stimulus_modality,
                            number_of_stimuli=stimulus_number_of_stimuli,
                            mode_of_presentation=mode_of_presentation,
                            duration=stimulus_duration,
                            soa=stimulus_soa,
                        )
                    )
                    is_match = True
                else:
                    continue

            if not is_match:
                raise MissingStimulusCategoryError(
                    f"{sub_category} (index {index}) invalid for stimulus categories {possible_categories_for_sub_category}"
                )

    elif is_multiple_categories_and_singular_numerics:
        stimulus_duration, stimulus_soa = check_numeric_values(index, stimuli_duration_data[0], stimuli_soa_data[0])
        stimulus_modality = stimuli_modality_data[0]
        stimulus_number_of_stimuli = stimuli_number_of_stimuli_data[0]
        for idx in range(len_category):
            stimulus_category = check_category(index, stimuli_category_data[idx])
            stimulus_sub_category = check_sub_category(index, stimulus_category, stimuli_sub_category_data[idx])

            resolved_stimuli.append(
                UnconResolvedStimulusData(
                    category=stimulus_category,
                    sub_category=stimulus_sub_category,
                    modality=stimulus_modality,
                    number_of_stimuli=stimulus_number_of_stimuli,
                    mode_of_presentation=mode_of_presentation,
                    duration=stimulus_duration,
                    soa=stimulus_soa,
                )
            )

    elif is_no_sub_category:
        stimulus_category = check_category(index, stimuli_category_data[0])
        stimulus_duration, stimulus_soa = check_numeric_values(index, stimuli_duration_data[0], stimuli_soa_data[0])
        stimulus_modality = stimuli_modality_data[0]
        stimulus_number_of_stimuli = stimuli_number_of_stimuli_data[0]
        resolved_stimuli.append(
            UnconResolvedStimulusData(
                category=stimulus_category,
                sub_category=None,
                modality=stimulus_modality,
                number_of_stimuli=stimulus_number_of_stimuli,
                mode_of_presentation=mode_of_presentation,
                duration=stimulus_duration,
                soa=stimulus_soa,
            )
        )

    else:
        raise IncoherentStimuliDataError(f"incoherent data for prime stimuli; index: {index}")

    return resolved_stimuli


def categorize_prime_stimulus_data(item: dict):
    stimuli_category_data = clean_list_from_data(item["Stimuli Category"])
    stimuli_sub_category_data = clean_list_from_data(item["Stimuli Sub-category"])
    stimuli_duration_data = clean_list_from_data(item["Stimuli Duration"], integer=True)
    stimuli_soa_data = clean_list_from_data(item["Stimuli SOA"], integer=True)
    stimuli_modalities, stimuli_number_of_stimuli_list = resolve_common_stimulus_data(item=item, prime=True)

    len_category = len(stimuli_category_data)
    len_sub_category = len(stimuli_sub_category_data)
    len_duration = len(stimuli_duration_data)
    len_soa = len(stimuli_soa_data)
    len_modality = len(stimuli_modalities)
    len_number_of_stimuli = len(stimuli_number_of_stimuli_list)

    try:
        is_same_length = len_category == len_duration == len_soa == len_sub_category and stimuli_sub_category_data != [
            ""
        ]
        is_multiple_sub_categories_and_multiple_numerics = (
            len_duration == len_soa == len_sub_category and len_sub_category > len_category == 1
        )
        is_multiple_sub_categories_and_singular_numerics = (
            len_sub_category > len_category == len_duration == len_soa == 1
        )
        is_multiple_categories_and_singular_numerics = len_duration == len_soa == 1 < len_category
        is_no_sub_category = uncon_stimulus_categories[
            stimuli_category_data[0]
        ] == [] and stimuli_sub_category_data == [""]
        is_multiple_categories_and_multiple_sub_categories = (
            len_sub_category > len_category > 1 and len_duration == len_soa == 1
        )
        is_multiple_modalities = len_modality > 1
        is_multiple_number_of_stimuli = len_number_of_stimuli > 1

    except KeyError:
        raise MissingValueInStimuliError(f"missing value: {stimuli_category_data, stimuli_sub_category_data}")

    return ResolvedCategoriesBoolean(
        is_multiple_categories_and_multiple_sub_categories=is_multiple_categories_and_multiple_sub_categories,
        is_multiple_categories_and_singular_numerics=is_multiple_categories_and_singular_numerics,
        is_multiple_sub_categories_and_multiple_numerics=is_multiple_sub_categories_and_multiple_numerics,
        is_multiple_sub_categories_and_singular_numerics=is_multiple_sub_categories_and_singular_numerics,
        is_no_sub_category=is_no_sub_category,
        is_same_length=is_same_length,
        len_category=len_category,
        len_sub_category=len_sub_category,
        stimuli_category_data=stimuli_category_data,
        stimuli_sub_category_data=stimuli_sub_category_data,
        stimuli_duration_data=stimuli_duration_data,
        stimuli_soa_data=stimuli_soa_data,
        stimuli_modalities_data=stimuli_modalities,
        stimuli_number_of_stimuli_data=stimuli_number_of_stimuli_list,
        is_multiple_modalities=is_multiple_modalities,
        is_multiple_number_of_stimuli=is_multiple_number_of_stimuli,
    )


def check_numeric_values(index: str, stimulus_duration: str, stimulus_soa: str) -> Optional[tuple]:
    try:
        resolved_stimulus_soa = float(stimulus_soa)
        resolved_stimulus_duration = float(stimulus_duration)

        return resolved_stimulus_duration, resolved_stimulus_soa

    except TypeError:
        raise StimulusDurationError(f"invalid stimulus numeric data, {index}")


def check_sub_category(index: str, stimulus_category: str, sub_category: str) -> Optional[str]:
    if sub_category not in uncon_stimulus_categories[stimulus_category]:
        raise MissingStimulusCategoryError(
            f"{sub_category} (index {index}) invalid for stimulus category {stimulus_category}"
        )
    else:
        stimulus_sub_category = sub_category

        return stimulus_sub_category


def check_category(index: str, stimulus_category: str) -> Optional[str]:
    if stimulus_category not in uncon_stimulus_categories.keys():
        raise MissingStimulusCategoryError(f"invalid stimulus category {stimulus_category} (index {index})")
    else:
        return stimulus_category


def resolve_common_stimulus_data(item: dict, prime: bool):
    stimuli_modalities = []
    stimuli_number_of_stimuli_list = []
    if prime:
        stimuli_modality_data = clean_list_from_data(item["Stimuli Modality"])
        stimuli_number_of_stimuli_data = clean_list_from_data(
            item["Stimuli Number of different stimuli used in the experiment"], integer=True
        )

    else:
        stimuli_modality_data = clean_list_from_data(item["Stimuli Modality 2"])
        stimuli_number_of_stimuli_data = clean_list_from_data(
            item["Stimuli Number of different stimuli used in the experiment 2"], integer=True
        )

    for modality in stimuli_modality_data:
        if modality not in uncon_stimulus_modalities:
            raise StimulusModalityError(f"{modality} not valid for stimulus modality")
        else:
            stimuli_modalities.append(modality)
    for number in stimuli_number_of_stimuli_data:
        try:
            stimulus_number_of_stimuli = int(number)
            stimuli_number_of_stimuli_list.append(stimulus_number_of_stimuli)

        except TypeError:
            raise StimulusDurationError(f"invalid stimulus numeric data: {number}")

    return stimuli_modalities, stimuli_number_of_stimuli_list


def resolve_uncon_target_stimuli(item: dict, index: str):
    resolved_stimuli = []

    stimuli_category_data = clean_list_from_data(item["Stimuli Category 2"])
    stimuli_sub_category_data = clean_list_from_data(item["Stimuli Sub-category 2"])

    if stimuli_category_data == ["missing"] or stimuli_sub_category_data == ["missing"]:
        return resolved_stimuli

    # resolve modalities
    stimuli_modalities, stimuli_number_of_stimuli_list = resolve_common_stimulus_data(item=item, prime=False)

    # resolve fields that might have multiple entries
    len_category = len(stimuli_category_data)
    len_sub_category = len(stimuli_sub_category_data)
    len_modality = len(stimuli_modalities)
    len_number_of_stimuli = len(stimuli_number_of_stimuli_list)
    is_same_length = len_category == len_sub_category and stimuli_sub_category_data != [""]
    is_no_sub_category = uncon_stimulus_categories[stimuli_category_data[0]] == [] and stimuli_sub_category_data == [""]
    is_multiple_sub_categories = len_sub_category > len_category >= 1
    is_multiple_modalities = len_modality > 1
    is_multiple_number_of_stimuli = len_number_of_stimuli > 1

    if is_same_length:
        for idx in range(len(stimuli_category_data)):
            stimulus_category = check_category(index, stimuli_category_data[idx])
            stimulus_sub_category = check_sub_category(index, stimulus_category, stimuli_sub_category_data[idx])
            if is_multiple_modalities:
                try:
                    stimulus_modality = stimuli_modalities[idx]
                except IndexError:
                    raise IncoherentStimuliDataError(
                        "number of modality values is lower than number of stimuli categories"
                    )
            else:
                stimulus_modality = stimuli_modalities[0]
            if is_multiple_number_of_stimuli:
                stimulus_number_of_stimuli = stimuli_number_of_stimuli_list[idx]
            else:
                stimulus_number_of_stimuli = stimuli_number_of_stimuli_list[0]

            resolved_stimuli.append(
                UnconResolvedStimulusData(
                    category=stimulus_category,
                    sub_category=stimulus_sub_category,
                    modality=stimulus_modality,
                    number_of_stimuli=stimulus_number_of_stimuli,
                    mode_of_presentation=None,
                    duration=None,
                    soa=None,
                )
            )

    elif is_no_sub_category:
        stimulus_category = check_category(index, stimuli_category_data[0])
        stimulus_modality = stimuli_modalities[0]
        stimulus_number_of_stimuli = stimuli_number_of_stimuli_list[0]

        resolved_stimuli.append(
            UnconResolvedStimulusData(
                category=stimulus_category,
                sub_category=None,
                modality=stimulus_modality,
                number_of_stimuli=stimulus_number_of_stimuli,
                mode_of_presentation=None,
                duration=None,
                soa=None,
            )
        )

    elif is_multiple_sub_categories:
        stimulus_category = check_category(index, stimuli_category_data[0])
        stimulus_modality = stimuli_modalities[0]
        stimulus_number_of_stimuli = stimuli_number_of_stimuli_list[0]

        for sub_category in stimuli_sub_category_data:
            stimulus_sub_category = check_sub_category(index, stimulus_category, sub_category)

            resolved_stimuli.append(
                UnconResolvedStimulusData(
                    category=stimulus_category,
                    sub_category=stimulus_sub_category,
                    modality=stimulus_modality,
                    number_of_stimuli=stimulus_number_of_stimuli,
                    mode_of_presentation=None,
                    duration=None,
                    soa=None,
                )
            )

    else:
        raise IncoherentStimuliDataError(f"incoherent data for target stimuli; index: {index}")

    return resolved_stimuli


def resolve_uncon_stimuli_metadata(item, index):
    is_target_stimuli_data = (
        str(
            item[
                "Stimuli Are there also non-suppressed stimuli that participants had to provide a response to (i.e., a target)?"
            ]
        )
        .lower()
        .strip()
    )
    is_target_stimuli_same_as_prime_data = (
        str(item["Stimuli Is the non-suppressed stimulus the same as the suppressed stimulus?"]).lower().strip()
    )

    is_target_stimuli_same_as_prime = False

    if is_target_stimuli_data == "yes":
        is_target_stimuli = True
        if is_target_stimuli_same_as_prime_data == "yes":
            is_target_stimuli_same_as_prime = True
        elif is_target_stimuli_same_as_prime_data == "no":
            is_target_stimuli_same_as_prime = False
    elif is_target_stimuli_data == "no":
        is_target_stimuli = False
        is_target_stimuli_same_as_prime = False
    else:
        raise StimulusMetadataError(f"bad stimulus metadata: {index}")

    return UnconResolvedStimuliMetadata(
        is_target_stimuli=is_target_stimuli, is_target_same_as_prime=is_target_stimuli_same_as_prime
    )


UnconResolvedStimulusData = namedtuple(
    "UnconResolvedStimulusData",
    ["category", "sub_category", "modality", "mode_of_presentation", "duration", "soa", "number_of_stimuli"],
)
UnconResolvedStimuliMetadata = namedtuple(
    "UnconResolvedStimuliMetadata", ["is_target_stimuli", "is_target_same_as_prime"]
)
ResolvedCategoriesBoolean = namedtuple(
    "ResolvedCategoriesBoolean",
    [
        "is_multiple_categories_and_multiple_sub_categories",
        "is_multiple_categories_and_singular_numerics",
        "is_multiple_sub_categories_and_multiple_numerics",
        "is_multiple_sub_categories_and_singular_numerics",
        "is_no_sub_category",
        "is_same_length",
        "len_category",
        "len_sub_category",
        "stimuli_category_data",
        "stimuli_sub_category_data",
        "stimuli_duration_data",
        "stimuli_soa_data",
        "stimuli_modalities_data",
        "stimuli_number_of_stimuli_data",
        "is_multiple_modalities",
        "is_multiple_number_of_stimuli",
    ],
)
