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


def resolve_uncon_stimuli(item: dict, index: str, prime: bool):
    NULL_VALUES = ["", "NA", "N/A", "n/a", "missing", "NaN"]

    resolved_stimuli = []

    # resolve singular data that exists for both prime and target stimuli
    if prime:
        stimuli_modality_data = str(item["Stimuli Modality"]).strip()
        stimuli_number_of_stimuli_data = item["Stimuli Number of different stimuli used in the experiment"]

    else:
        stimuli_modality_data = str(item["Stimuli Modality 2"]).strip()
        stimuli_number_of_stimuli_data = item["Stimuli Number of different stimuli used in the experiment 2"]

    if stimuli_modality_data not in uncon_stimulus_modalities:
        raise StimulusModalityError(
            f"{stimuli_modality_data} (index {index}) not valid for stimulus modality, prime: {prime}"
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

    if prime:
        stimuli_category_data = clean_list_from_data(item["Stimuli Category"])
        stimuli_sub_category_data = clean_list_from_data(item["Stimuli Sub-category"])
        stimuli_duration_data = clean_list_from_data(item["Stimuli Duration"], integer=True)
        stimuli_soa_data = clean_list_from_data(item["Stimuli SOA"], integer=True)
        stimuli_mode_of_presentation_data = str(item["Stimuli Mode of presentation"]).strip().lower()

        # resolve singular data for prime stimuli
        if stimuli_mode_of_presentation_data == "liminal":
            mode_of_presentation = PresentationModeChoices.LIMINAL
        elif stimuli_mode_of_presentation_data == "subliminal":
            mode_of_presentation = PresentationModeChoices.SUBLIMINAL
        else:
            raise StimulusModeOfPresentationError(
                f"{stimuli_mode_of_presentation_data} (index {index}) not valid for stimulus mode of presentation"
            )

        # resolve fields that might have multiple entries for prime stimuli
        len_category = len(stimuli_category_data)
        len_sub_category = len(stimuli_sub_category_data)
        len_duration = len(stimuli_duration_data)
        len_soa = len(stimuli_soa_data)

        is_same_length = len_category == len_duration == len_soa == len_sub_category and stimuli_sub_category_data != [""]
        is_multiple_sub_categories_and_multiple_numerics = len_duration == len_soa == len_sub_category > len_category
        is_multiple_sub_categories_and_singular_numerics = len_sub_category > len_category == len_duration == len_soa == 1
        is_multiple_categories_and_singular_numerics = len_duration == len_soa == 1 < len_category
        is_no_sub_category = len_category > len_sub_category or stimuli_sub_category_data == [""]

        if is_same_length:
            for idx in range(len_category):
                indexed_stimuli_category = stimuli_category_data[idx]
                indexed_stimuli_sub_category = stimuli_sub_category_data[idx]
                indexed_stimuli_duration = stimuli_duration_data[idx]
                indexed_stimuli_soa = stimuli_soa_data[idx]

                if indexed_stimuli_category not in uncon_stimulus_categories.keys():
                    raise MissingStimulusCategoryError(
                        f"invalid stimulus category {indexed_stimuli_category} (index {index})"
                    )
                else:
                    stimulus_category = indexed_stimuli_category
                    if indexed_stimuli_sub_category not in uncon_stimulus_categories[stimulus_category]:
                        raise MissingStimulusCategoryError(
                            f"{indexed_stimuli_sub_category} (index {index}) invalid for stimulus category {stimulus_category}"
                        )
                    else:
                        stimulus_sub_category = indexed_stimuli_sub_category

                try:
                    if indexed_stimuli_duration in NULL_VALUES:  # TODO: after data is full, change to throw error
                        stimulus_duration = 0
                    else:
                        stimulus_duration = float(indexed_stimuli_duration)

                    if indexed_stimuli_soa in NULL_VALUES:
                        stimulus_soa = 0
                    else:
                        stimulus_soa = float(indexed_stimuli_soa)

                except TypeError:
                    raise StimulusDurationError(f"invalid stimulus numeric data, {index}")

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
            stimulus_category = stimuli_category_data[0]
            if stimulus_category not in uncon_stimulus_categories.keys():
                raise MissingStimulusCategoryError(
                    f"invalid stimulus category {stimulus_category} (index {index})"
                )

            for idx in range(len_sub_category):
                indexed_stimuli_sub_category = stimuli_sub_category_data[idx]
                indexed_stimuli_duration = stimuli_duration_data[idx]
                indexed_stimuli_soa = stimuli_soa_data[idx]

                if indexed_stimuli_sub_category not in uncon_stimulus_categories[stimulus_category]:
                    raise MissingStimulusCategoryError(
                        f"{indexed_stimuli_sub_category} (index {index}) invalid for stimulus category {stimulus_category}"
                    )
                else:
                    stimulus_sub_category = indexed_stimuli_sub_category

                try:
                    if indexed_stimuli_duration in NULL_VALUES:  # TODO: after data is full, change to throw error
                        stimulus_duration = 0
                    else:
                        stimulus_duration = float(indexed_stimuli_duration)

                    if indexed_stimuli_soa in NULL_VALUES:
                        stimulus_soa = 0
                    else:
                        stimulus_soa = float(indexed_stimuli_soa)

                except TypeError:
                    raise StimulusDurationError(f"invalid stimulus numeric data, {index}")

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
            stimulus_category = stimuli_category_data[0]
            stimulus_duration = stimuli_duration_data[0]
            stimulus_soa = stimuli_soa_data[0]

            if stimulus_category not in uncon_stimulus_categories.keys():
                raise MissingStimulusCategoryError(
                    f"invalid stimulus category {stimulus_category} (index {index})"
                )
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

            for sub_category in stimuli_sub_category_data:
                if sub_category not in uncon_stimulus_categories[stimulus_category]:
                    raise MissingStimulusCategoryError(
                        f"{sub_category} (index {index}) invalid for stimulus category {stimulus_category}"
                    )
                else:
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

        elif is_multiple_categories_and_singular_numerics:
            stimulus_duration = stimuli_duration_data[0]
            stimulus_soa = stimuli_soa_data[0]

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

            for idx in range(len_category):
                indexed_stimuli_category = stimuli_category_data[idx]
                indexed_stimuli_sub_category = stimuli_sub_category_data[idx]

                if indexed_stimuli_category not in uncon_stimulus_categories.keys():
                    raise MissingStimulusCategoryError(
                        f"invalid stimulus category {indexed_stimuli_category} (index {index})"
                    )
                else:
                    stimulus_category = indexed_stimuli_category
                    if indexed_stimuli_sub_category not in uncon_stimulus_categories[stimulus_category]:
                        raise MissingStimulusCategoryError(
                            f"{indexed_stimuli_sub_category} (index {index}) invalid for stimulus category {stimulus_category}"
                        )
                    else:
                        stimulus_sub_category = indexed_stimuli_sub_category

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
            stimulus_category = stimuli_category_data[0]
            stimulus_duration = stimuli_duration_data[0]
            stimulus_soa = stimuli_soa_data[0]

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

            if stimulus_category not in uncon_stimulus_categories.keys():
                raise MissingStimulusCategoryError(
                    f"invalid stimulus category {stimulus_category} (index {index})"
                )

            if len(uncon_stimulus_categories[stimulus_category]) != 0:
                raise MissingStimulusCategoryError(
                    f"stimulus category {stimulus_category} missing sub-category (index {index})"
                )

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
            raise IncoherentStimuliDataError(f"incoherent data for stimuli; index: {index} prime:{prime}")

    else:
        stimuli_category_data = clean_list_from_data(item["Stimuli Category 2"])
        stimuli_sub_category_data = clean_list_from_data(item["Stimuli Sub-category 2"])

        # resolve fields that might have multiple entries for target stimuli
        len_category = len(stimuli_category_data)
        len_sub_category = len(stimuli_sub_category_data)
        is_no_sub_category = len(uncon_stimulus_categories[stimuli_category_data[0]]) == 0 and len(stimuli_sub_category_data[0]) == 0
        is_multiple_sub_categories = len_sub_category > len_category == 1

        if len_category == len_sub_category > 0 and stimuli_sub_category_data != [""]:
            for idx in range(len(stimuli_category_data)):
                indexed_stimuli_category = stimuli_category_data[idx]
                indexed_stimuli_sub_category = stimuli_sub_category_data[idx]

                if indexed_stimuli_category not in uncon_stimulus_categories.keys():
                    raise MissingStimulusCategoryError(
                        f"invalid stimulus category {indexed_stimuli_category} (index {index})"
                    )
                else:
                    stimulus_category = indexed_stimuli_category
                    if indexed_stimuli_sub_category not in uncon_stimulus_categories[stimulus_category]:
                        raise MissingStimulusCategoryError(
                            f"{indexed_stimuli_sub_category} (index {index}) invalid for stimulus category {stimulus_category}"
                        )
                    else:
                        stimulus_sub_category = indexed_stimuli_sub_category

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
            stimulus_category = stimuli_category_data[0]
            if stimulus_category not in uncon_stimulus_categories.keys():
                raise MissingStimulusCategoryError(
                    f"invalid stimulus category {stimulus_category} (index {index})"
                )

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
            stimulus_category = stimuli_category_data[0]
            if stimulus_category not in uncon_stimulus_categories.keys():
                raise MissingStimulusCategoryError(
                    f"invalid stimulus category {stimulus_category} (index {index})"
                )

            for sub_category in stimuli_sub_category_data:
                if sub_category not in uncon_stimulus_categories[stimulus_category]:
                    raise MissingStimulusCategoryError(
                        f"{sub_category} (index {index}) invalid for stimulus category {stimulus_category}"
                    )
                else:
                    stimulus_sub_category = sub_category

                resolved_stimuli.append(
                    UnconResolvedStimulusData(
                        category=stimulus_category,
                        sub_category=stimulus_sub_category,
                        modality=stimulus_modality,
                        number_of_stimuli=stimulus_number_of_stimuli,
                        mode_of_presentation=None,
                        duration=None,
                        soa=None,
                    ))

        else:
            raise IncoherentStimuliDataError(f"incoherent data for stimuli; index: {index} prime:{prime}")

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
