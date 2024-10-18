from collections import namedtuple

from django.core.exceptions import ObjectDoesNotExist

from contrast_api.choices import ExperimentTypeChoices
from contrast_api.data_migration_functionality.errors import IncoherentStimuliDataError, StimulusModalityError
from contrast_api.data_migration_functionality.studies_parsing_helpers import ProblemInStudyExistingDataException
from studies.models import Study
from uncontrast_studies.models import (
    UnConExperiment,
    UnConSpecificParadigm,
    UnConTask,
    UnConSuppressedStimulus,
    UnConTargetStimulus,
    UnConSuppressionMethodType,
    UnConSuppressionMethodSubType,
    UnConSuppressionMethod,
    UnConSample,
    UnConProcessingMainDomain,
    UnConProcessingDomain,
    UnConFinding,
    UnConsciousnessMeasurePhase,
    UnConsciousnessMeasureType,
    UnConsciousnessMeasureSubType,
    UnConsciousnessMeasure,
    UnConTaskType,
    UnConMainParadigm,
    UnConStimulusCategory,
    UnConStimulusSubCategory,
    UnConModalityType,
    UnConOutcome,
)
from uncontrast_studies.parsers.consciousness_measure_parser import resolve_consciousness_measures
from uncontrast_studies.parsers.uncon_data_parsers import (
    resolve_uncon_paradigm,
    resolve_uncon_task_type,
    resolve_uncon_processing_domains,
)
from uncontrast_studies.parsers.stimulus_parser import (
    resolve_uncon_prime_stimuli,
    resolve_uncon_stimuli_metadata,
    is_target_duplicate,
    resolve_uncon_target_stimuli,
)
from uncontrast_studies.parsers.suppression_method_parser import resolve_uncon_suppression_method
from uncontrast_studies.parsers.sample_parser import resolve_uncon_sample
from uncontrast_studies.parsers.finding_parser import resolve_uncon_findings

ExperimentDuplicate = namedtuple("ExperimentDuplicateTuple", ["key", "id"])


def create_uncon_experiment(item: dict, index):
    try:
        if item["DOI"] != "missing":
            study = Study.objects.get(DOI=item["DOI"])
        else:
            study = Study.objects.get(DOI=item["StudyID"])  # TODO: change back to DOI
    except ObjectDoesNotExist:
        raise ProblemInStudyExistingDataException()

    paradigm_data = resolve_uncon_paradigm(item, index)
    main_paradigm = UnConMainParadigm.objects.get(name=paradigm_data.main)
    paradigm = UnConSpecificParadigm.objects.get(main=main_paradigm, name=paradigm_data.specific)

    experiment = UnConExperiment.objects.create(
        study=study,
        type=ExperimentTypeChoices.BEHAVIORAL,
        paradigm=paradigm,
    )

    return experiment


def create_prime_stimulus(experiment, prime_data, is_target_stimuli: bool):
    category = UnConStimulusCategory.objects.get(name=prime_data.category)
    try:
        modality = UnConModalityType.objects.get(name=prime_data.modality)
    except UnConModalityType.DoesNotExist:
        raise StimulusModalityError()

    if prime_data.sub_category:
        sub_category = UnConStimulusSubCategory.objects.get(name=prime_data.sub_category, parent=category)
    else:
        sub_category = None

    suppressed_stimulus = UnConSuppressedStimulus.objects.create(
        experiment=experiment,
        category=category,
        sub_category=sub_category,
        modality=modality,
        mode_of_presentation=prime_data.mode_of_presentation,
        duration=prime_data.duration,
        soa=prime_data.soa,
        number_of_stimuli=prime_data.number_of_stimuli,
        is_target_stimulus=is_target_stimuli,
    )

    return suppressed_stimulus


def create_target_stimulus(experiment, suppressed_stimulus, stimulus_data, is_target_same_as_suppressed_stimulus: bool):
    category = UnConStimulusCategory.objects.get(name=stimulus_data.category)
    modality = UnConModalityType.objects.get(name=stimulus_data.modality)
    if stimulus_data.sub_category:
        sub_category = UnConStimulusSubCategory.objects.get(name=stimulus_data.sub_category, parent=category)
    else:
        sub_category = None

    UnConTargetStimulus.objects.create(
        experiment=experiment,
        suppressed_stimulus=suppressed_stimulus,
        is_target_same_as_suppressed_stimulus=is_target_same_as_suppressed_stimulus,
        category=category,
        sub_category=sub_category,
        modality=modality,
        number_of_stimuli=stimulus_data.number_of_stimuli,
    )


def process_uncon_experiment(item: dict):
    experiment_index = item["exp"]
    experiment = create_uncon_experiment(item=item, index=experiment_index)

    # tasks
    task_types = resolve_uncon_task_type(item=item, index=experiment_index)
    for task_type in task_types:
        task = UnConTaskType.objects.get(name=task_type)
        UnConTask.objects.create(experiment=experiment, type=task)

    # samples
    sample = resolve_uncon_sample(item=item, index=experiment_index)
    UnConSample.objects.create(
        experiment=experiment,
        type=sample.sample_type,
        size_included=sample.included_size,
        size_total=sample.total_size,
        size_excluded=sample.excluded_size or 0,
    )

    # stimuli
    resolved_prime_stimuli = resolve_uncon_prime_stimuli(item=item, index=experiment_index)
    is_target_stimuli, is_target_same_as_prime = resolve_uncon_stimuli_metadata(item=item, index=experiment_index)
    if is_target_stimuli:
        resolved_target_stimuli = resolve_uncon_target_stimuli(item=item, index=experiment_index)
        if is_target_same_as_prime and is_target_duplicate(item=item):
            for prime_data in resolved_prime_stimuli:
                suppressed_stimulus = create_prime_stimulus(experiment, prime_data, is_target_stimuli)
                create_target_stimulus(experiment, suppressed_stimulus, prime_data, is_target_same_as_prime)
        elif len(resolved_prime_stimuli) == len(resolved_target_stimuli) and not is_target_same_as_prime:
            for idx in range(len(resolved_prime_stimuli)):
                suppressed_stimulus = create_prime_stimulus(experiment, resolved_prime_stimuli[idx], is_target_stimuli)
                create_target_stimulus(
                    experiment, suppressed_stimulus, resolved_target_stimuli[idx], is_target_same_as_prime
                )
        else:
            raise IncoherentStimuliDataError(
                f"target supposed to be same as prime stimulus, but it's different; index {experiment_index}"
            )
    else:
        for prime_data in resolved_prime_stimuli:
            create_prime_stimulus(experiment, prime_data, is_target_stimuli)

    # suppression_methods
    suppression_method_data = resolve_uncon_suppression_method(item=item, index=experiment_index)
    for line in suppression_method_data:
        main = UnConSuppressionMethodType.objects.get(name=line.main)
        if line.specific is None:
            UnConSuppressionMethod.objects.create(experiment=experiment, type=main, sub_type=None)
        else:
            specific = UnConSuppressionMethodSubType.objects.get(name=line.specific, parent=main)
            UnConSuppressionMethod.objects.create(experiment=experiment, type=main, sub_type=specific)

    # processing domains
    processing_domain_data = resolve_uncon_processing_domains(item=item, index=experiment_index)
    for processing_domain in processing_domain_data:
        main_domain = UnConProcessingMainDomain.objects.get(name=processing_domain)
        UnConProcessingDomain.objects.create(experiment=experiment, main=main_domain)

    # findings
    finding_data = resolve_uncon_findings(item=item, index=experiment_index)
    for finding in finding_data:
        outcome = UnConOutcome.objects.get(name=finding.outcome)
        UnConFinding.objects.create(
            experiment=experiment,
            outcome=outcome,
            is_significant=finding.is_significant,
            is_important=finding.is_important,
            number_of_trials=finding.number_of_trials,
        )
        if finding.notes:
            experiment.experiment_findings_notes.add(f"{finding.notes}; ")

    # consciousness measures
    consciousness_measures_data = resolve_consciousness_measures(item=item, index=experiment_index)
    for consciousness_measure in consciousness_measures_data:
        phase = UnConsciousnessMeasurePhase.objects.get(name=consciousness_measure.phase)
        main_type = UnConsciousnessMeasureType.objects.get(name=consciousness_measure.type)
        if consciousness_measure.sub_type:
            sub_type = UnConsciousnessMeasureSubType.objects.get(name=consciousness_measure.sub_type, type=main_type)
        else:
            sub_type = None
        UnConsciousnessMeasure.objects.create(
            experiment=experiment,
            phase=phase,
            type=main_type,
            sub_type=sub_type,
            number_of_trials=consciousness_measure.number_of_trials,
            number_of_participants_in_awareness_test=consciousness_measure.number_of_awareness_participants,
            is_cm_same_participants_as_task=consciousness_measure.is_cm_pax_same_as_task,
            is_performance_above_chance=consciousness_measure.is_performance_above_chance,
            is_trial_excluded_based_on_measure=consciousness_measure.is_trial_excluded_based_on_measure,
        )
        if consciousness_measure.notes:
            experiment.consciousness_measures_notes.add(f"{consciousness_measure.notes}; ")

    return experiment
