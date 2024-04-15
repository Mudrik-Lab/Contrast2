import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from configuration.initial_setup import current_child_theories, techniques, finding_tags_map
from contrast_api.choices import (
    InterpretationsChoices,
    ExperimentTypeChoices,
    TypeOfConsciousnessChoices,
    ReportingChoices,
    DirectionChoices,
)
from contrast_api.data_migration_functionality.errors import MissingStimulusCategoryError, ParadigmDataException, \
    IncoherentSampleDataError, ProblemInCMExistingDataException, ParadigmError
from studies.models import (
    Theory,
    Technique,
    Paradigm,
    ConsciousnessMeasureType,
    ConsciousnessMeasurePhaseType,
    ConsciousnessMeasure,
    MeasureType,
    Measure,
    Sample,
    TaskType,
    Task,
    ModalityType,
    FindingTagFamily,
    FindingTagType,
    FindingTag,
    Study,
    Experiment,
)
from studies.models.stimulus import StimulusCategory, StimulusSubCategory, Stimulus
from studies.parsers.historic_data_helpers import (
    get_paradigms_from_data,
    get_consciousness_measure_type_and_phase_from_data,
    get_measures_from_data,
    get_sample_from_data,
    parse_task_types,
    get_stimuli_from_data,
    parse_theory_driven_from_data,
)
from studies.parsers.parsing_findings_Contrast2 import (
    parse,
    FrequencyFinding,
    TemporalFinding,
    SpatialFinding,
    FindingTagDataError,
)
from contrast_api.data_migration_functionality.studies_parsing_helpers import (
    ProblemInStudyExistingDataException,
)

logger = logging.getLogger("Contrast2")


def create_experiment(item: dict):
    # start with straight-forward data (study, results summary, type)
    try:
        study = Study.objects.get(DOI=item["Paper.DOI"])
    except ObjectDoesNotExist:
        raise ProblemInStudyExistingDataException()

    results_summary = item["Findings.Summary"]
    experiment_type = ExperimentTypeChoices.NEUROSCIENTIFIC

    # resolve choices fields (theory_driven, type_of_consciousness, is_reporting)
    theories = current_child_theories
    theory_driven, theory_driven_theories = parse_theory_driven_from_data(item, theories)

    type_of_consciousness = ""
    type_of_consciousness_choice = item["State - Content"]
    if type_of_consciousness_choice in ["0", 0]:
        type_of_consciousness = TypeOfConsciousnessChoices.STATE
    elif type_of_consciousness_choice in ["1", 1]:
        type_of_consciousness = TypeOfConsciousnessChoices.CONTENT
    elif type_of_consciousness_choice in ["2", 2]:
        type_of_consciousness = TypeOfConsciousnessChoices.BOTH

    is_reporting = ""
    reporting_choice = item["Experimental paradigms.Report"]
    if reporting_choice in ["0", 0]:
        is_reporting = ReportingChoices.NO_REPORT
    elif reporting_choice in ["1", 1]:
        is_reporting = ReportingChoices.REPORT
    elif reporting_choice in ["2", 2]:
        is_reporting = ReportingChoices.BOTH

    tasks_notes = item["Task.Description"]
    consciousness_measures_notes = item["Measures of consciousness.Description"]
    stimuli_notes = item["Stimuli Features.Description"]

    experiment = Experiment.objects.create(
        study=study,
        type_of_consciousness=type_of_consciousness,
        results_summary=results_summary,
        is_reporting=is_reporting,
        theory_driven=theory_driven,
        type=experiment_type,
        tasks_notes=tasks_notes,
        stimuli_notes=stimuli_notes,
        consciousness_measures_notes=consciousness_measures_notes,
    )

    logger.info(f"experiment {experiment.id} for study {study.DOI} created")

    return experiment, theory_driven_theories


def process_row(item: dict):
    experiment, theory_driven_theories = create_experiment(item=item)

    # resolve and add ManyToMany fields (theory-driven theories, interpretations, paradigms, techniques)
    for theory in theory_driven_theories:
        theory = Theory.objects.get(name=theory)
        experiment.theory_driven_theories.add(theory)

    theories = current_child_theories
    interpretation = ""
    for theory in theories:
        for key, value in item.items():
            if theory not in key:
                continue
            if value in ["1", 1]:
                interpretation = InterpretationsChoices.PRO
            elif value in ["0", 0]:
                interpretation = InterpretationsChoices.CHALLENGES
            elif value == "X":
                interpretation = InterpretationsChoices.NEUTRAL
        interpretation_theory = Theory.objects.get(name=theory)
        experiment.interpretations.add(interpretation_theory, through_defaults={"type": interpretation})

    techniques_in_historic_data = []
    for technique in techniques:
        if technique not in item["Techniques"]:
            continue
        parsed_technique = Technique.objects.get(name=technique)
        techniques_in_historic_data.append(parsed_technique)

    for technique in techniques_in_historic_data:
        experiment.techniques.add(technique)

    try:
        paradigms_in_data = get_paradigms_from_data(item)
        main_paradigms = []
        specific_paradigms = []

        for paradigm in paradigms_in_data:
            name = paradigm.name
            if paradigm.parent is None:
                main_paradigm = Paradigm.objects.get(name=name, parent=None, sub_type=None)
                main_paradigms.append(main_paradigm)
            else:
                main_paradigm = Paradigm.objects.get(name=paradigm.parent, parent=None, sub_type=None)
                if paradigm.sub_type is None:
                    specific_paradigm = Paradigm.objects.get(name=name, parent=main_paradigm, sub_type=None)
                    specific_paradigms.append(specific_paradigm)
                else:
                    sub_type = paradigm.sub_type
                    specific_paradigm = Paradigm.objects.get(name=name, parent=main_paradigm, sub_type=sub_type)
                    specific_paradigms.append(specific_paradigm)

        for specific_paradigm in specific_paradigms:
            if specific_paradigm.parent in main_paradigms:
                experiment.paradigms.add(specific_paradigm)
            else:
                raise ParadigmError(f"main paradigm {specific_paradigm.parent} doesn't exist")

    except (ParadigmError, ObjectDoesNotExist):
        raise ParadigmDataException(
            f"paradigm error for {item['Experimental paradigms.Main Paradigm']} or {item['Experimental paradigms.Specific Paradigm']}"
        )

    # resolve and create consciousness measures
    consciousness_measures_from_data = get_consciousness_measure_type_and_phase_from_data(item)
    try:
        for consciousness_measure in consciousness_measures_from_data:
            consciousness_type = consciousness_measure.type
            consciousness_phase = consciousness_measure.phase
            consciousness_measure_type = ConsciousnessMeasureType.objects.get(name=consciousness_type)
            consciousness_measure_phase = ConsciousnessMeasurePhaseType.objects.get(name=consciousness_phase)
            ConsciousnessMeasure.objects.create(
                experiment=experiment, phase=consciousness_measure_phase, type=consciousness_measure_type
            )
    except ObjectDoesNotExist:
        raise ProblemInCMExistingDataException()

    # resolve and create finding measures
    measures = get_measures_from_data(item)
    for measure in measures:
        measure_type = measure.measure_type
        notes = measure.measure_notes
        measure_name = MeasureType.objects.get(name=measure_type)
        Measure.objects.create(experiment=experiment, type=measure_name, notes=notes)

    # resolve and create samples
    try:
        samples = get_sample_from_data(item)
        sample_notes_list = []
        for sample in samples:
            sample_type = sample.sample_type
            total_size = int(sample.total_size)
            included_size = int(sample.included_size)

            Sample.objects.create(
                experiment=experiment, type=sample_type, total_size=total_size, size_included=included_size
            )
            note = sample.note
            if note is not None:
                sample_notes_list.append(note)
        sample_notes_string = "; ".join(map(str, sample_notes_list))
        experiment.sample_notes = sample_notes_string
        experiment.save()

    except ValueError as error:
        logger.exception(f"{error} while processing sample data")
        raise IncoherentSampleDataError

    # resolve and create tasks
    for parsed_task_type in parse_task_types(item):
        task_type = TaskType.objects.get(name=parsed_task_type)

        Task.objects.create(experiment=experiment, type=task_type)

    # resolve and create stimuli
    stimuli_from_data = get_stimuli_from_data(item)
    stimulus_sub_category = ""
    for stimulus in stimuli_from_data:
        if (stimulus.duration is None) or (stimulus.duration == "None"):
            duration = None
        else:
            duration = float(stimulus.duration)
        try:
            modality_type = ""
            if stimulus.modality:
                modality_type = ModalityType.objects.get(name=stimulus.modality)
            stimulus_category = StimulusCategory.objects.get(name=stimulus.category)
            if (stimulus.sub_category == "") or (stimulus.sub_category is None):
                stimulus_sub_category = None
            else:
                stimulus_sub_category = StimulusSubCategory.objects.get(
                    name=stimulus.sub_category, parent=stimulus_category
                )
            Stimulus.objects.create(
                experiment=experiment,
                category=stimulus_category,
                sub_category=stimulus_sub_category,
                modality=modality_type,
                duration=duration,
            )

        except (ObjectDoesNotExist, ValueError) as error:
            logger.exception(f"{error} while processing stimuli data")
            raise MissingStimulusCategoryError()

    # resolve and create findings
    findings_ncc_tags = item["Findings.NCC Tags"]
    try:
        findings = parse(findings_ncc_tags)
        for finding in findings:
            resolved_tag_type = finding_tags_map[finding.tag]
            comment = finding.comment
            is_ncc = finding.is_NCC
            if finding.technique is not None:
                resolved_technique = finding.technique
                technique = Technique.objects.get(name=resolved_technique)
            elif len(techniques_in_historic_data) == 1:
                resolved_technique = techniques_in_historic_data[0]
                technique = Technique.objects.get(name=resolved_technique)
            else:
                technique = None

            if isinstance(finding, FrequencyFinding):
                family_name = "Frequency"
                family = FindingTagFamily.objects.get(name=family_name)
                tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                if finding.direction == "Negative":
                    direction = DirectionChoices.NEGATIVE
                else:
                    direction = DirectionChoices.POSITIVE

                FindingTag.objects.create(
                    experiment=experiment,
                    family=family,
                    type=tag_type,
                    onset=finding.onset,
                    offset=finding.offset,
                    band_lower_bound=finding.band_low,
                    band_higher_bound=finding.band_high,
                    notes=comment,
                    analysis_type=finding.analysis,
                    direction=direction,
                    technique=technique,
                    is_NCC=is_ncc,
                )

            elif isinstance(finding, TemporalFinding):
                family_name = "Temporal"
                family = FindingTagFamily.objects.get(name=family_name)
                tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                FindingTag.objects.create(
                    experiment=experiment,
                    family=family,
                    type=tag_type,
                    onset=finding.onset,
                    offset=finding.offset,
                    notes=comment,
                    technique=technique,
                    is_NCC=is_ncc,
                )

            elif isinstance(finding, SpatialFinding):
                family_name = "Spatial Areas"
                family = FindingTagFamily.objects.get(name=family_name)
                tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                FindingTag.objects.create(
                    experiment=experiment,
                    family=family,
                    type=tag_type,
                    AAL_atlas_tag=finding.area,
                    notes=comment,
                    technique=technique,
                    is_NCC=is_ncc,
                )

            else:
                family_name = "miscellaneous"
                family = FindingTagFamily.objects.get(name=family_name)
                tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                FindingTag.objects.create(
                    experiment=experiment, family=family, type=tag_type, notes=comment, is_NCC=is_ncc
                )
    except (
        ValueError,
        IndexError,
        KeyError,
        FindingTagType.DoesNotExist,
        Technique.DoesNotExist,
        IntegrityError,
    ) as error:
        logger.exception(f"{error} while processing finding tag data {finding}")
        raise FindingTagDataError()
