from collections import namedtuple

from configuration.uncontrast_initial_data_types import uncon_paradigms, uncon_tasks, uncon_stimulus_categories, \
    uncon_stimulus_modalities, uncon_suppression_methods, uncon_processing_domains, uncon_finding_outcomes
from contrast_api.choices import PresentationModeChoices, UnConSampleChoices
from contrast_api.data_migration_functionality.errors import ParadigmError, StimulusMetadataError, TaskTypeError, \
    MissingStimulusCategoryError, StimulusModalityError, StimulusModeOfPresentationError, StimulusDurationError, \
    SuppressionMethodError, SampleTypeError, SampleSizeError, IncoherentSampleDataError, ProcessingDomainError, \
    FindingError

UnconResolvedParadigmData = namedtuple("UnconParadigmFromData", ["main", "specific"])
UnconResolvedStimuliMetadata = namedtuple("UnconResolvedStimuliMetadata",
                                          ["is_target_stimuli", "is_target_same_as_prime"])
UnconResolvedStimulusData = namedtuple("UnconResolvedStimulusData",
                                       ["category", "sub_category", "modality", "mode_of_presentation",
                                        "duration", "soa", "number_of_stimuli"])
UnconResolvedSuppressionMethodData = namedtuple("UnconResolvedSuppressionMethodData", ["main", "specific"])
UnConResolvedSample = namedtuple("UnConResolvedSample", ["sample_type", "total_size", "included_size", "excluded_size"])
UnConResolvedFinding = namedtuple("UnConResolvedFinding", ["outcome", "is_significant", "is_important", "number_of_trials"])


def resolve_uncon_paradigm(item):
    main_paradigm = str(item["Paradigms Main paradigm"]).strip()
    specific_paradigm = str(item["Paradigms Specific paradigm"]).strip()

    if main_paradigm not in uncon_paradigms.keys():
        raise ParadigmError(f"missing main paradigm: {main_paradigm}.")
    if specific_paradigm not in uncon_paradigms.values():
        raise ParadigmError(f"missing specific paradigm: {specific_paradigm}.")

    return UnconResolvedParadigmData(main=main_paradigm, specific=specific_paradigm)


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


def resolve_uncon_sample(item, index):
    pass


def resolve_uncon_task(item: dict, index: str):
    task_data = str(item["Tasks Type"]).strip()

    if task_data not in uncon_tasks:
        raise TaskTypeError(f"task error for {index}: {task_data}")

    return task_data


def resolve_uncon_stimuli(item: dict, index: str, prime: bool):
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

    null_values = ["", "NA", "N/A", "missing"]

    try:
        if stimuli_duration_data in null_values:
            stimulus_duration = None
        else:
            stimulus_duration = float(stimuli_duration_data)

        if stimuli_soa_data in null_values:
            stimulus_soa = None
        else:
            stimulus_soa = float(stimuli_soa_data)

        if stimuli_number_of_stimuli_data in null_values:
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


def resolve_uncon_suppression_method(item: dict, index: str):
    suppression_methods_list = []
    main_methods = []
    specific_methods = []
    main_suppression_methods_data = str(item["Suppression method Main suppression method"]).split(";")
    specific_suppression_methods_data = str(item["Suppression method Specific suppression method"]).split(";")

    for main_method in main_suppression_methods_data:
        if main_method.strip() in uncon_suppression_methods.keys():
            resolved_main_method = main_method.strip()
            main_methods.append(resolved_main_method)
        else:
            raise SuppressionMethodError(f"invalid main suppression method {main_method}, index {index}")

    for specific_method in specific_suppression_methods_data:
        is_match = False
        for main_method in main_methods:
            if specific_method.strip() in uncon_suppression_methods[main_method]:
                resolved_specific_method = specific_method.strip()
                specific_methods.append(resolved_specific_method)
                is_match = True
            else:
                continue
        if not is_match:
            raise SuppressionMethodError(f"invalid specific suppression method {specific_method}, index {index}")

    if len(main_methods) == 0:
        raise SuppressionMethodError(f"missing main suppression method, index {index}")

    for resolved_main_method in main_methods:
        if len(uncon_suppression_methods[resolved_main_method]) == 0 or len(specific_methods) == 0:
            suppression_method = UnconResolvedSuppressionMethodData(main=resolved_main_method, specific=None)
            suppression_methods_list.append(suppression_method)
        else:
            for resolved_specific_method in specific_methods:
                if resolved_specific_method in uncon_suppression_methods[resolved_main_method]:
                    suppression_method = UnconResolvedSuppressionMethodData(main=resolved_main_method, specific=resolved_specific_method)
                    suppression_methods_list.append(suppression_method)
                else:
                    raise SuppressionMethodError(f"specific suppression method {resolved_specific_method} is invalid "
                                                 f"for main suppression method: {resolved_main_method}, index {index}")

    return suppression_methods_list


def resolve_uncon_samples(item: dict, index: str):
    samples_list = []
    resolved_sample_types = []
    resolved_sample_total_size = []
    resolved_sample_included_size = []
    resolved_sample_excluded_size = []
    samples_type_data = str(item["Samples Type"]).split(";")
    samples_total_data = str(item["Samples Total"]).split(";")
    samples_included_data = str(item["Samples Included"]).split(";")
    samples_excluded_data = str(item["Samples Excluded"]).split(";")

    for sample_type in samples_type_data:
        if sample_type.strip().lower() == "healthy adults":
            resolved_sample_type = UnConSampleChoices.HEALTHY_ADULTS
        elif sample_type.strip().lower() == "healthy college students":
            resolved_sample_type = UnConSampleChoices.HEALTHY_COLLEGE_STUDENTS
        elif sample_type.strip().lower() == "children":
            resolved_sample_type = UnConSampleChoices.CHILDREN
        elif sample_type.strip().lower() == "patients adults":
            resolved_sample_type = UnConSampleChoices.PATIENTS_ADULTS
        elif sample_type.strip().lower() == "patients children":
            resolved_sample_type = UnConSampleChoices.PATIENTS_CHILDREN
        elif sample_type.strip().lower() == "non human":
            resolved_sample_type = UnConSampleChoices.NON_HUMAN
        elif sample_type.strip().lower() == "computer":
            resolved_sample_type = UnConSampleChoices.COMPUTER
        else:
            raise SampleTypeError(f"invalid sample type {sample_type}, index {index}")
        resolved_sample_types.append(resolved_sample_type)

    for total_size in samples_total_data:
        try:
            resolved_total_size = int(total_size)
            resolved_sample_total_size.append(resolved_total_size)
        except TypeError:
            raise SampleSizeError(f"invalid sample size {total_size}, index {index}")

    for included_size in samples_included_data:
        try:
            resolved_included_size = int(included_size)
            resolved_sample_included_size.append(resolved_included_size)
        except TypeError:
            raise SampleSizeError(f"invalid sample size {included_size}, index {index}")

    for excluded_size in samples_excluded_data:
        try:
            resolved_excluded_size = int(excluded_size)
            resolved_sample_excluded_size.append(resolved_excluded_size)
        except TypeError:
            raise SampleSizeError(f"invalid sample size {excluded_size}, index {index}")

    if len(samples_type_data) == len(samples_total_data) == len(samples_included_data) == len(samples_excluded_data):
        for idx in range(len(resolved_sample_types)):
            if samples_excluded_data[idx] == 0:
                sample = UnConResolvedSample(sample_type=resolved_sample_types[idx], total_size=samples_total_data[idx],
                                             included_size=samples_included_data[idx], excluded_size=None)
                samples_list.append(sample)
            else:
                sample = UnConResolvedSample(sample_type=resolved_sample_types[idx], total_size=samples_total_data[idx],
                                             included_size=samples_included_data[idx], excluded_size=samples_excluded_data[idx])
                samples_list.append(sample)

    else:
        raise IncoherentSampleDataError(f"incoherent sample data, index {index}")

    return samples_list


def resolve_uncon_findings(item: dict, index: str):
    # TODO: change to multiple findings per experiment
    resolved_findings = []
    outcome_data = str(item["Experiment's Findings Outcome"])
    significance_data = str(item["Experiment's Findings Is the effect significant?"])
    number_of_trials_data = item["Experiment's Findings Number of trials"]

    if outcome_data.strip() not in uncon_finding_outcomes:
        raise FindingError(f"invalid outcome {outcome_data}, index {index}")
    else:
        outcome = outcome_data.strip()

    if significance_data.strip().lower() == "yes":
        is_significant = True
    elif significance_data.strip().lower() == "no":
        is_significant = False
    else:
        raise FindingError(f"invalid significance {significance_data}, index {index}")

    try:
        if number_of_trials_data == "" or number_of_trials_data == "missing":
            number_of_trials = 1
        number_of_trials = int(number_of_trials_data)
    except TypeError:
        raise FindingError(f"invalid number of trials {number_of_trials_data}, index {index}")

    resolved_findings.append(UnConResolvedFinding(outcome=outcome, is_significant=is_significant, is_important=True,
                                number_of_trials=number_of_trials))
    return resolved_findings


def resolve_uncon_processing_domains(item: dict, index: str):
    resolved_processing_domains = []
    processing_domain_data = str(item["Processing domain"]).split(";")
    for processing_domain_data in processing_domain_data:
        main_domain_data = processing_domain_data.strip()
        if main_domain_data in uncon_processing_domains:
            resolved_processing_domains.append(main_domain_data)
        else:
            raise ProcessingDomainError(f"invalid processing domain {main_domain_data}, index: {index}")

    return resolved_processing_domains
