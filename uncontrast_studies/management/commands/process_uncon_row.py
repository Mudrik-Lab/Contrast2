from collections import namedtuple

from django.core.exceptions import ObjectDoesNotExist

from contrast_api.choices import ExperimentTypeChoices
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
)
from uncontrast_studies.parsers.consciousness_measure_parser import resolve_consciousness_measures
from uncontrast_studies.parsers.uncon_data_parsers import (
    resolve_uncon_paradigm,
    resolve_uncon_task,
    resolve_uncon_processing_domains,
)
from uncontrast_studies.parsers.stimulus_parser import resolve_uncon_stimuli, resolve_uncon_stimuli_metadata
from uncontrast_studies.parsers.suppression_method_parser import resolve_uncon_suppression_method
from uncontrast_studies.parsers.sample_parser import resolve_uncon_sample
from uncontrast_studies.parsers.finding_parser import resolve_uncon_findings

ExperimentDuplicate = namedtuple("ExperimentDuplicateTuple", ["key", "id"])


def create_uncon_experiment(item: dict, index):
    try:
        if item["Paper.DOI"]:
            study = Study.objects.get(DOI=item["Paper.DOI"])
        else:
            study = Study.objects.get(DOI=item["StudyID"])  # TODO: change back to DOI
    except ObjectDoesNotExist:
        raise ProblemInStudyExistingDataException()

    paradigm_data = resolve_uncon_paradigm(item, index)
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


def process_uncon_row(item: dict):
    experiment_index = item["exp"]
    experiment = create_uncon_experiment(item=item, index=experiment_index)

    # tasks
    task_types = resolve_uncon_task(item=item, index=experiment_index)
    for task_type in task_types:
        task, created = UnConTaskType.objects.get_or_create(name=task_type)
        UnConTask.objects.get_or_create(experiment=experiment, type=task)

    # samples
    samples = resolve_uncon_sample(item=item, index=experiment_index)
    for sample in samples:
        UnConSample.objects.get_or_create(
            experiment=experiment,
            type=sample.sample_type,
            size_included=sample.included_size,
            size_total=sample.total_size,
            size_excluded=sample.excluded_size,
        )

    # stimuli
    prime_stimuli = resolve_uncon_stimuli(item=item, index=experiment_index, prime=True)
    UnConSuppressedStimulus.objects.get_or_create(
        experiment=experiment,
        category=prime_stimuli.category,
        sub_category=prime_stimuli.sub_category,
        modality=prime_stimuli.modality,
        mode_of_presentation=prime_stimuli.mode_of_presentation,
        duration=prime_stimuli.duration,
        soa=prime_stimuli.soa,
        number_of_stimuli=prime_stimuli.number_of_stimuli,
    )
    if experiment.is_target_stimulus:
        if experiment.is_target_same_as_suppressed_stimulus:
            UnConTargetStimulus.objects.get_or_create(
                experiment=experiment,
                category=prime_stimuli.category,
                sub_category=prime_stimuli.sub_category,
                modality=prime_stimuli.modality,
                number_of_stimuli=prime_stimuli.number_of_stimuli,
            )
        else:
            target_stimuli = resolve_uncon_stimuli(item=item, index=experiment_index, prime=False)
            UnConTargetStimulus.objects.get_or_create(
                experiment=experiment,
                category=target_stimuli.category,
                sub_category=target_stimuli.sub_category,
                modality=target_stimuli.modality,
                number_of_stimuli=target_stimuli.number_of_stimuli,
            )
    # suppression_methods
    suppression_method_data = resolve_uncon_suppression_method(item=item, index=experiment_index)
    for line in suppression_method_data:
        if line.specific:
            main, created = UnConSuppressionMethodType.objects.get_or_create(name=line.main)
            specific, created = UnConSuppressionMethodSubType.objects.get_or_create(name=line.specific, parent=main)
            UnConSuppressionMethod.objects.get_or_create(experiment=experiment, type=main, sub_type=specific)
        else:
            main, created = UnConSuppressionMethodType.objects.get_or_create(name=line.main)
            UnConSuppressionMethod.objects.get_or_create(experiment=experiment, type=main, sub_type=None)

    # processing domains
    processing_domain_data = resolve_uncon_processing_domains(item=item, index=experiment_index)
    for processing_domain in processing_domain_data:
        main_domain, created = UnConProcessingMainDomain.objects.get_or_create(name=processing_domain)
        UnConProcessingDomain.objects.create(experiment=experiment, main=main_domain)

    # findings
    finding_data = resolve_uncon_findings(item=item, index=experiment_index)
    for finding in finding_data:
        UnConFinding.objects.create(
            experiment=experiment,
            outcome=finding.outcome,
            is_significant=finding.is_significant,
            is_important=finding.is_important,
            number_of_trials=finding.number_of_trials,
        )
        if finding.notes:
            experiment.experiment_findings_notes.add(f"{finding.notes}; ")

    # consciousness measures
    consciousness_measures_data = resolve_consciousness_measures(item=item, index=experiment_index)
    for consciousness_measure in consciousness_measures_data:
        phase, created = UnConsciousnessMeasurePhase.objects.get_or_create(name=consciousness_measure.phase)
        main_type, created = UnConsciousnessMeasureType.objects.get_or_create(name=consciousness_measure.type)
        if consciousness_measure.sub_type:
            sub_type, created = UnConsciousnessMeasureSubType.objects.get_or_create(
                name=consciousness_measure.sub_type, type=main_type
            )
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
