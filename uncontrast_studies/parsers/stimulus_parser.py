from collections import namedtuple

from configuration.uncontrast_initial_data_types import uncon_stimulus_categories, uncon_stimulus_modalities
from contrast_api.choices import PresentationModeChoices
from contrast_api.data_migration_functionality.errors import MissingStimulusCategoryError, StimulusModalityError, \
    StimulusModeOfPresentationError, StimulusDurationError, StimulusMetadataError


def resolve_uncon_stimuli(item: dict, index: str, prime: bool):
    NULL_VALUES = ["", "NA", "N/A", "n/a", "missing"]

    # TODO: convert to returning a list for mulitple results
    if prime:
        stimuli_category_data = str(item["Stimuli Category"]).strip()
        stimuli_sub_category_data = str(item["Stimuli Sub-category"]).strip()
        stimuli_modality_data = str(item["Stimuli Modality"]).strip()
        stimuli_number_of_stimuli_data = item["Stimuli Number of different stimuli used in the experiment"]
    else:
        stimuli_category_data = str(item["Stimuli Category 2"]).strip()
        stimuli_sub_category_data = str(item["Stimuli Sub-category 2"]).strip()
        stimuli_modality_data = str(item["Stimuli Modality 2"]).strip()
        stimuli_number_of_stimuli_data = item["Stimuli Number of different stimuli used in the experiment 2"]

    stimuli_mode_of_presentation_data = str(item["Stimuli Mode of presentation"]).strip().lower()
    stimuli_duration_data = str(item["Stimuli Duration"]).strip().lower()
    stimuli_soa_data = item["Stimuli SOA"]

    if stimuli_category_data not in uncon_stimulus_categories.keys():
        raise MissingStimulusCategoryError(f"{stimuli_category_data} (index {index}) not valid for stimulus category")
    else:
        stimulus_category = stimuli_category_data

    if stimuli_sub_category_data not in uncon_stimulus_categories[stimuli_category_data]:
        raise MissingStimulusCategoryError(
            f"{stimuli_sub_category_data} (index {index}) not valid for stimulus category {stimuli_category_data}")
    else:
        stimulus_sub_category = stimuli_sub_category_data

    if stimuli_modality_data not in uncon_stimulus_modalities:
        raise StimulusModalityError(f"{stimuli_modality_data} (index {index}) not valid for stimulus modality")
    else:
        stimulus_modality = stimuli_modality_data

    if stimuli_mode_of_presentation_data == "liminal":
        mode_of_presentation = PresentationModeChoices.LIMINAL
    elif stimuli_mode_of_presentation_data == "subliminal":
        mode_of_presentation = PresentationModeChoices.SUBLIMINAL
    else:
        raise StimulusModeOfPresentationError(
            f"{stimuli_mode_of_presentation_data} (index {index}) not valid for stimulus mode of presentation")

    try:
        if stimuli_duration_data in NULL_VALUES:
            stimulus_duration = None
        else:
            stimulus_duration = float(stimuli_duration_data)

        if stimuli_soa_data in NULL_VALUES:
            stimulus_soa = None
        else:
            stimulus_soa = float(stimuli_soa_data)

        if stimuli_number_of_stimuli_data in NULL_VALUES:
            stimulus_number_of_stimuli = None
        else:
            stimulus_number_of_stimuli = int(stimuli_number_of_stimuli_data)

    except TypeError:
        raise StimulusDurationError(f"invalid stimulus numeric data, {index}")

    return UnconResolvedStimulusData(category=stimulus_category, sub_category=stimulus_sub_category,
                                     modality=stimulus_modality,
                                     mode_of_presentation=mode_of_presentation, duration=stimulus_duration,
                                     soa=stimulus_soa,
                                     number_of_stimuli=stimulus_number_of_stimuli)


def resolve_uncon_stimuli_metadata(item, index):
    is_target_stimuli_data = str(item["Stimuli Are there also non-suppressed stimuli?"]).lower().strip()
    is_target_stimuli_same_as_prime_data = str(
        item["Stimuli Is the non-suppressed stimulus the same as prime?"]
    ).lower().strip()

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


UnconResolvedStimulusData = namedtuple("UnconResolvedStimulusData",
                                       ["category", "sub_category", "modality", "mode_of_presentation",
                                        "duration", "soa", "number_of_stimuli"])
UnconResolvedStimuliMetadata = namedtuple("UnconResolvedStimuliMetadata",
                                          ["is_target_stimuli", "is_target_same_as_prime"])
