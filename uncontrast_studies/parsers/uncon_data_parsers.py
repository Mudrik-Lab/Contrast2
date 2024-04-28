from collections import namedtuple

from configuration.uncontrast_initial_data_types import uncon_paradigms
from contrast_api.data_migration_functionality.errors import ParadigmError, StimulusMetadataError

UnconResolvedParadigmData = namedtuple("UnconParadigmFromData", ["main", "specific"])
UnconResolvedStimuliMetadata = namedtuple("UnconParadigmFromData", ["is_target_stimuli", "is_target_same_as_prime"])


def resolve_uncon_paradigm(item):
    main_paradigm = item["Paradigms Main paradigm"]
    specific_paradigm = item["Paradigms Specific paradigm"]

    if main_paradigm not in uncon_paradigms.keys():
        raise ParadigmError(f"missing main paradigm: {main_paradigm}.")
    if specific_paradigm not in uncon_paradigms.values():
        raise ParadigmError(f"missing specific paradigm: {specific_paradigm}.")

    return UnconResolvedParadigmData(main=main_paradigm, specific=specific_paradigm)


def resolve_uncon_stimuli_metadata(item, index):
    is_target_stimuli_data = str(item["Stimuli Are there also non-suppressed stimuli?"]).lower()
    is_target_stimuli_same_as_prime_data = str(
        item["Stimuli Is the non-suppressed stimulus the same as prime?"]
    ).lower()

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
