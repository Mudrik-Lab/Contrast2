from collections import namedtuple

from django.core.exceptions import ObjectDoesNotExist

from contrast_api.choices import ExperimentTypeChoices
from contrast_api.data_migration_functionality.studies_parsing_helpers import ProblemInStudyExistingDataException
from studies.models import Study
from uncontrast_studies.models import UnConExperiment, UnConSpecificParadigm, UnConTask, UnConSuppressedStimulus, \
    UnConTargetStimulus, UnConSuppressionMethodType, UnConSuppressionMethodSubType, UnConSuppressionMethod, UnConSample
from uncontrast_studies.parsers.uncon_data_parsers import resolve_uncon_paradigm, resolve_uncon_stimuli_metadata, \
    resolve_uncon_task, resolve_uncon_stimuli, resolve_uncon_suppression_method, resolve_uncon_samples, \
    resolve_uncon_findings, resolve_uncon_processing_domains

ExperimentDuplicate = namedtuple("ExperimentDuplicateTuple", ["key", "id"])


def create_uncon_experiment(item: dict, index):
    try:
        if item["Paper.DOI"]:
            study = Study.objects.get(DOI=item["Paper.DOI"])
        else:
            study = Study.objects.get(DOI=item["StudyID"])  # TODO: change back to DOI
    except ObjectDoesNotExist:
        raise ProblemInStudyExistingDataException()

    paradigm_data = resolve_uncon_paradigm(item)
    paradigm, created = UnConSpecificParadigm.objects.get_or_create(
        main=paradigm_data.main, name=paradigm_data.specific
    )
    stimuli_metadata = resolve_uncon_stimuli_metadata(item, index)

    experiment, created = UnConExperiment.objects.get_or_create(
        study=study,
        type=ExperimentTypeChoices.BEHAVIORAL,
        paradigm=paradigm,
        is_target_stimulus=stimuli_metadata.is_target_stimulus,
        is_target_same_as_suppressed_stimulus=stimuli_metadata.is_target_same_as_prime,
    )

    return experiment


def process_uncon_row(item: dict, duplicated_experiments: dict):
    study_id = item["StudyID"]
    experiment_index = item["exp"]
    composit_experiment_index = f"{study_id}, {experiment_index}"

    # first we check for pre-existing experiment data, creating new experiment if non-existing, else fetching existing data
    if composit_experiment_index not in duplicated_experiments.keys():
        experiment = create_uncon_experiment(item=item, index=composit_experiment_index)
        duplicated_experiment = ExperimentDuplicate(key=composit_experiment_index, id=experiment.id)
    else:
        duplicated_experiment = None
        experiment_id = duplicated_experiments[composit_experiment_index]
        experiment = UnConExperiment.objects.get(id=experiment_id)

    # TODO: create experiment-dependent objects: consciousness measures, findings, processing domains.
    # tasks
    task_type = resolve_uncon_task(item=item, index=composit_experiment_index)
    UnConTask.objects.get_or_create(experiment=experiment, type=task_type)

    # samples
    samples = resolve_uncon_samples(item=item, index=composit_experiment_index)
    for sample in samples:
        UnConSample.objects.get_or_create(experiment=experiment, type=sample.sample_type, size_included=sample.included_size,
                                          size_total=sample.total_size, size_excluded=sample.excluded_size,)

    # stimuli
    prime_stimuli = resolve_uncon_stimuli(item=item, index=composit_experiment_index, prime=True)
    UnConSuppressedStimulus.objects.get_or_create(experiment=experiment, category=prime_stimuli.category, sub_category=prime_stimuli.sub_category,
                                                  modality=prime_stimuli.modality, mode_of_presentation=prime_stimuli.mode_of_presentation,
                                                  duration=prime_stimuli.duration, soa=prime_stimuli.soa, number_of_stimuli=prime_stimuli.number_of_stimuli)
    if experiment.is_target_stimulus:
        if experiment.is_target_same_as_suppressed_stimulus:
            UnConTargetStimulus.objects.get_or_create(experiment=experiment, category=prime_stimuli.category, sub_category=prime_stimuli.sub_category,
                                                      modality=prime_stimuli.modality, number_of_stimuli=prime_stimuli.number_of_stimuli)
        else:
            target_stimuli = resolve_uncon_stimuli(item=item, index=composit_experiment_index, prime=False)
            UnConTargetStimulus.objects.get_or_create(experiment=experiment, category=target_stimuli.category, sub_category=target_stimuli.sub_category,
                                                      modality=target_stimuli.modality, number_of_stimuli=target_stimuli.number_of_stimuli)
    # suppression_methods
    suppression_method_data = resolve_uncon_suppression_method(item=item, index=composit_experiment_index)
    for line in suppression_method_data:
        if line.specific:
            main, created = UnConSuppressionMethodType.objects.get_or_create(name=line.main)
            specific, created = UnConSuppressionMethodSubType.objects.get_or_create(name=line.specific, parent=main)
            UnConSuppressionMethod.objects.get_or_create(experiment=experiment, type=main, sub_type=specific)
        else:
            main, created = UnConSuppressionMethodType.objects.get_or_create(name=line.main)
            UnConSuppressionMethod.objects.get_or_create(experiment=experiment, type=main, sub_type=None)

    # processing domains
    processing_domain_data = resolve_uncon_processing_domains(item=item, index=composit_experiment_index)
    for processing_domain in processing_domain_data:
        pass

    # findings
    finding_data = resolve_uncon_findings(item=item, index=composit_experiment_index)





    return duplicated_experiment
