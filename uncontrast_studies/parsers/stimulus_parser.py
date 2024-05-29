from collections import namedtuple

from configuration.uncontrast_initial_data_types import uncon_stimulus_categories, uncon_stimulus_modalities
from contrast_api.choices import PresentationModeChoices
from contrast_api.data_migration_functionality.errors import (
    MissingStimulusCategoryError,
    StimulusModalityError,
    StimulusModeOfPresentationError,
    StimulusDurationError,
    StimulusMetadataError,
    IncoherentStimuliDataError,
)
from uncontrast_studies.parsers.uncon_data_parsers import clean_list_from_data


def is_target_duplicate(item: dict):
    stimuli_category_data = item["Stimuli Category"]
    stimuli_sub_category_data = item["Stimuli Sub-category"]
    stimuli_modality_data = item["Stimuli Modality"]
    stimuli_number_of_stimuli_data = item["Stimuli Number of different stimuli used in the experiment"]

    stimuli_category_data_2 = item["Stimuli Category 2"]
    stimuli_sub_category_data_2 = item["Stimuli Sub-category 2"]
    stimuli_modality_data_2 = item["Stimuli Modality 2"]
    stimuli_number_of_stimuli_data_2 = item["Stimuli Number of different stimuli used in the experiment 2"]

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

    stimuli_category_data = clean_list_from_data(item["Stimuli Category"])
    stimuli_sub_category_data = clean_list_from_data(item["Stimuli Sub-category"])
    stimuli_duration_data = clean_list_from_data(item["Stimuli Duration"], integer=True)
    stimuli_soa_data = clean_list_from_data(item["Stimuli SOA"], integer=True)
    stimuli_mode_of_presentation_data = str(item["Stimuli Mode of presentation"]).strip().lower()

    # resolve singular data
    stimulus_modality, stimulus_number_of_stimuli = resolve_singular_stimulus_data(item=item, index=index, prime=True)

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
    ) = categorize_prime_stimulus_data(item)

    if is_same_length:
        for idx in range(len_category):
            stimulus_category = check_category(index, stimuli_category_data[idx])
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

    elif is_multiple_sub_categories_and_multiple_numerics:
        stimulus_category = check_category(index, stimuli_category_data[0])

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

    len_category = len(stimuli_category_data)
    len_sub_category = len(stimuli_sub_category_data)
    len_duration = len(stimuli_duration_data)
    len_soa = len(stimuli_soa_data)

    is_same_length = len_category == len_duration == len_soa == len_sub_category and stimuli_sub_category_data != [""]
    is_multiple_sub_categories_and_multiple_numerics = (
        len_duration == len_soa == len_sub_category and len_sub_category > len_category == 1
    )
    is_multiple_sub_categories_and_singular_numerics = len_sub_category > len_category == len_duration == len_soa == 1
    is_multiple_categories_and_singular_numerics = len_duration == len_soa == 1 < len_category
    is_no_sub_category = uncon_stimulus_categories[stimuli_category_data[0]] == [] and stimuli_sub_category_data == [""]
    is_multiple_categories_and_multiple_sub_categories = (
        len_sub_category > len_category > 1 and len_duration == len_soa == 1
    )

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
    )


def check_numeric_values(index: str, stimulus_duration, stimulus_soa):
    NULL_VALUES = ["", "NA", "N/A", "n/a", "missing", "NaN"]

    try:
        if stimulus_duration in NULL_VALUES:  # TODO: after data is full, change to throw error
            stimulus_duration = 0
        else:
            stimulus_duration = float(stimulus_duration)

        if stimulus_soa in NULL_VALUES:
            stimulus_soa = 0
        else:
            stimulus_soa = float(stimulus_soa)

    except TypeError:
        raise StimulusDurationError(f"invalid stimulus numeric data, {index}")

    return stimulus_duration, stimulus_soa


def check_sub_category(index: str, stimulus_category: str, sub_category: str) -> str:
    if sub_category not in uncon_stimulus_categories[stimulus_category]:
        raise MissingStimulusCategoryError(
            f"{sub_category} (index {index}) invalid for stimulus category {stimulus_category}"
        )
    else:
        stimulus_sub_category = sub_category

        return stimulus_sub_category


def check_category(index: str, stimulus_category: str) -> str:
    if stimulus_category not in uncon_stimulus_categories.keys():
        raise MissingStimulusCategoryError(f"invalid stimulus category {stimulus_category} (index {index})")
    else:
        return stimulus_category


def resolve_singular_stimulus_data(item: dict, index: str, prime: bool):
    NULL_VALUES = ["", "NA", "N/A", "n/a", "missing", "NaN"]

    if prime:
        stimuli_modality_data = str(item["Stimuli Modality"]).strip()
        stimuli_number_of_stimuli_data = item["Stimuli Number of different stimuli used in the experiment"]

    else:
        stimuli_modality_data = str(item["Stimuli Modality 2"]).strip()
        stimuli_number_of_stimuli_data = item["Stimuli Number of different stimuli used in the experiment 2"]

    if stimuli_modality_data not in uncon_stimulus_modalities:
        if prime:
            raise StimulusModalityError(
                f"{stimuli_modality_data} (index {index}) not valid for prime stimulus modality"
            )
        else:
            raise StimulusModalityError(
                f"{stimuli_modality_data} (index {index}) not valid for target stimulus modality"
            )
    else:
        stimulus_modality = stimuli_modality_data

    try:
        if stimuli_number_of_stimuli_data in NULL_VALUES:
            stimulus_number_of_stimuli = 0
        else:
            stimulus_number_of_stimuli = int(stimuli_number_of_stimuli_data)

    except TypeError:
        raise StimulusDurationError(f"invalid stimulus numeric data, {index}")

    return stimulus_modality, stimulus_number_of_stimuli


def resolve_uncon_target_stimuli(item: dict, index: str):
    resolved_stimuli = []

    stimuli_category_data = clean_list_from_data(item["Stimuli Category 2"])
    stimuli_sub_category_data = clean_list_from_data(item["Stimuli Sub-category 2"])

    # resolve singular data
    stimulus_modality, stimulus_number_of_stimuli = resolve_singular_stimulus_data(item=item, index=index, prime=False)

    # resolve fields that might have multiple entries
    len_category = len(stimuli_category_data)
    len_sub_category = len(stimuli_sub_category_data)
    is_same_length = len_category == len_sub_category and stimuli_sub_category_data != [""]
    is_no_sub_category = uncon_stimulus_categories[stimuli_category_data[0]] == [] and stimuli_sub_category_data == [""]
    is_multiple_sub_categories = len_sub_category > len_category == 1

    if is_same_length:
        for idx in range(len(stimuli_category_data)):
            stimulus_category = check_category(index, stimuli_category_data[idx])
            stimulus_sub_category = check_sub_category(index, stimulus_category, stimuli_sub_category_data[idx])

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

    if is_target_stimuli_data == "yes":
        is_target_stimuli = True
    elif is_target_stimuli_data == "no":
        is_target_stimuli = False
    else:
        raise StimulusMetadataError(f"bad stimulus metadata: {index}")

    if is_target_stimuli_same_as_prime_data == "yes":
        is_target_stimuli_same_as_prime = True
    elif is_target_stimuli_same_as_prime_data == "no":
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
    ],
)
