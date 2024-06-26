import logging
import re
from collections import namedtuple
from itertools import zip_longest
from typing import List

from configuration.initial_setup import (
    task_types_mapping,
    findings_measures,
    modalities,
    consciousness_measure_phases,
    consciousness_measure_types,
    paradigms,
    ambiguous_paradigms,
    main_paradigms,
    paradigm_sub_types,
    only_child_paradigms,
)
from contrast_api.choices import TheoryDrivenChoices, SampleChoices
from contrast_api.data_migration_functionality.errors import (
    ProblemInTheoryDrivenExistingDataException,
    IncoherentSampleDataError,
    SampleTypeError,
    IncoherentStimuliDataError,
    MissingValueInStimuliError,
    StimulusDurationError,
    ParadigmError,
)
from contrast_api.data_migration_functionality.helpers import add_to_notes, find_in_list, clean_text

logger = logging.getLogger("Contrast2")

ConsciousnessMeasureFromData = namedtuple("ConsciousnessMeasureFromData", ["type", "phase"])
ParadigmFromData = namedtuple("ParadigmFromData", ["parent", "name", "sub_type"])
MeasureFromData = namedtuple("MeasureFromData", ["measure_type", "measure_notes"])
StimulusFromData = namedtuple("StimulusFromData", ["category", "sub_category", "modality", "duration"])
SampleFromData = namedtuple("SampleFromData", ["sample_type", "total_size", "included_size", "note"])


def get_consciousness_measure_type_and_phase_from_data(item: dict) -> List[ConsciousnessMeasureFromData]:
    cm_phase_list = item["Measures of consciousness.Phase"].split("+")
    cm_type_list = item["Measures of consciousness.Type"].split("+")
    consciousness_measure_phase_lookup = consciousness_measure_phases
    consciousness_measure_type_lookup = consciousness_measure_types
    results = []

    resolved_phases = find_in_list(cm_phase_list, consciousness_measure_phase_lookup)
    resolved_types = find_in_list(cm_type_list, consciousness_measure_type_lookup)

    try:
        for resolved_phase, resolved_type in zip_longest(resolved_phases, resolved_types):
            if resolved_phase and resolved_type:
                results.append(ConsciousnessMeasureFromData(type=resolved_type, phase=resolved_phase))
            elif resolved_phase and not resolved_type:
                results.append(ConsciousnessMeasureFromData(type=resolved_types[0], phase=resolved_phase))
            elif resolved_type and not resolved_phase:
                results.append(ConsciousnessMeasureFromData(type=resolved_type, phase=resolved_phases[0]))
            else:
                break
    except IndexError as error:
        logger.exception(f"{error} while processing consciousness measure data (either type or phase)")
        print(f"phases: {resolved_phases}, types: {resolved_types}")
    return results


def parse_theory_driven_from_data(item: dict, theories: list) -> tuple:
    resolved_theory_driven_theories = []
    data = str(item["Theory Driven"])
    if "(" not in data:
        theory_driven_choice = data.strip()
        if theory_driven_choice in ["0", 0]:
            theory_driven = TheoryDrivenChoices.POST_HOC
            return theory_driven, resolved_theory_driven_theories
        else:
            raise ProblemInTheoryDrivenExistingDataException()

    theory_driven_data = data.split("(")
    theory_driven_choice = theory_driven_data[0].strip()
    theory_driven_theories = theory_driven_data[1].split(")")[0].split("&")

    if theory_driven_choice in ["1", 1]:
        theory_driven = TheoryDrivenChoices.MENTIONING
        for theory in theories:
            for theory_driven_theory in theory_driven_theories:
                if theory == theory_driven_theory.strip():
                    resolved_theory_driven_theories.append(theory)

    elif theory_driven_choice in ["2", 2]:
        theory_driven = TheoryDrivenChoices.DRIVEN
        for theory in theories:
            for theory_driven_theory in theory_driven_theories:
                if theory == theory_driven_theory.strip():
                    resolved_theory_driven_theories.append(theory)
    else:
        raise ProblemInTheoryDrivenExistingDataException()

    return theory_driven, resolved_theory_driven_theories


def parse_task_types(item: dict):
    parsed_task_types = []
    task_code_data = str(item["Task.Code"])
    tasks_codes_breakdown = task_code_data.split("+")
    for task_code in tasks_codes_breakdown:
        parsed_task_code = task_code.split("(")[0].strip()
        parsed_task = task_types_mapping[parsed_task_code]
        parsed_task_types.append(parsed_task)

    return parsed_task_types


def get_paradigms_from_data(item: dict) -> List[ParadigmFromData]:
    """
    return a list of main paradigms and specific paradigms. NOTE: this is not the final list of specific paradigms that gets into the data
    """
    paradigms_in_data = []

    parsed_main_paradigms = item["Experimental paradigms.Main Paradigm"].split("+")
    clean_main_paradigms = [clean_text(item.strip()) for item in parsed_main_paradigms]
    parsed_specific_paradigms = item["Experimental paradigms.Specific Paradigm"].split("+")
    clean_specific_paradigms = [clean_text(item.strip()) for item in parsed_specific_paradigms]

    # check for missing values and assign only-child paradigms if applicable
    if len(clean_specific_paradigms) < len(clean_main_paradigms):
        specific_paradigm_missing = True
        for item in clean_main_paradigms:
            if item in only_child_paradigms:
                only_child_paradigm = ParadigmFromData(name=item, parent=item, sub_type=None)
                paradigms_in_data.append(only_child_paradigm)
                parent = ParadigmFromData(name=item, parent=None, sub_type=None)
                paradigms_in_data.append(parent)
                clean_main_paradigms.remove(item)
                specific_paradigm_missing = False
            else:
                continue
        if specific_paradigm_missing:
            raise ParadigmError(f"missing specific paradigm for: {item}")

    # assign parent paradigms
    for paradigm in clean_main_paradigms:
        if paradigm not in main_paradigms:
            raise ParadigmError(f"missing paradigm: {paradigm}.")
        else:
            parent = ParadigmFromData(name=paradigm, parent=None, sub_type=None)
            paradigms_in_data.append(parent)
            if paradigm in only_child_paradigms:
                only_child_paradigm = ParadigmFromData(name=paradigm, parent=paradigm, sub_type=None)
                paradigms_in_data.append(only_child_paradigm)
                if str(paradigm) in clean_specific_paradigms:
                    clean_specific_paradigms.remove(str(paradigm))

    # assign specific paradigms to main paradigms
    for specific_paradigm in clean_specific_paradigms:
        no_parenthesis_specific_paradigm = specific_paradigm.split("(")[0].strip()
        if "(" not in specific_paradigm:
            for main_paradigm, group_of_specific_paradigms in paradigms.items():
                if specific_paradigm in group_of_specific_paradigms:
                    paradigm = ParadigmFromData(name=specific_paradigm, parent=main_paradigm, sub_type=None)
                    paradigms_in_data.append(paradigm)
                else:
                    continue
        else:
            classification_data = specific_paradigm.split("(")[1]
            if "," in classification_data:
                main_paradigm = classification_data.split(",")[0].strip()
                # parse subtype data
                subtype_data = classification_data.split(",")[1].replace(")", "")
                if "&" in subtype_data:
                    subtypes_list = subtype_data.split("&")
                    resolved_sub_types = [subtype.strip() for subtype in subtypes_list]
                else:
                    resolved_sub_types = [subtype_data.strip()]

                # check for match with existing subtypes from config
                matching_sub_types = []
                for list_of_sub_types in paradigm_sub_types.values():
                    matches = find_in_list(resolved_sub_types, list_of_sub_types)
                    matching_sub_types.extend(matches)
                for subtype in matching_sub_types:
                    paradigm = ParadigmFromData(
                        name=no_parenthesis_specific_paradigm, parent=main_paradigm, sub_type=subtype
                    )
                    paradigms_in_data.append(paradigm)

            else:
                # check for specific paradigms that still have ambiguous parent paradigm and resolve ambiguity
                parent = str(classification_data).split(")")[0].strip()
                if "Binocular" in specific_paradigm:  # only parent paradigm with parenthesis that's not ambiguous
                    paradigm = ParadigmFromData(
                        name=no_parenthesis_specific_paradigm, parent="Competition (Binocular)", sub_type=None
                    )
                    paradigms_in_data.append(paradigm)
                elif no_parenthesis_specific_paradigm in ambiguous_paradigms:
                    if "))" in specific_paradigm:
                        parent = specific_paradigm.replace("Bistable percepts (", "").replace("))", ")")
                        ambiguous_specific_paradigm = ParadigmFromData(
                            name=specific_paradigm, parent=parent, sub_type=None
                        )
                        paradigms_in_data.append(ambiguous_specific_paradigm)
                    elif (f"({parent})" in specific_paradigm) and (specific_paradigm in paradigms[parent]):
                        ambiguous_specific_paradigm = ParadigmFromData(
                            name=specific_paradigm, parent=parent, sub_type=None
                        )
                        paradigms_in_data.append(ambiguous_specific_paradigm)
                    else:
                        continue
                else:
                    paradigm = ParadigmFromData(name=no_parenthesis_specific_paradigm, parent=parent, sub_type=None)
                    paradigms_in_data.append(paradigm)

    return paradigms_in_data


def get_measures_from_data(item: dict) -> List[MeasureFromData]:
    measures_data = item["Findings.Measures"]
    measures_data_split = str(measures_data).split("+")
    measures_from_data = []
    for measure in measures_data_split:
        if "(" not in measure:
            measure_type_code = measure.strip()
            for key, value in findings_measures.items():
                if measure_type_code == key:
                    measure_type = value
                    measures_from_data.append(MeasureFromData(measure_type, ""))
        else:
            measure_type_code = measure.split("(")[0].strip()
            notes = measure.split("(")[1].split(")")[0].strip()
            for key, value in findings_measures.items():
                if measure_type_code == key:
                    measure_type = value
                    measures_from_data.append(MeasureFromData(measure_type, notes))

    return measures_from_data


def clean_duration_text(text):
    if "(" in text:
        main_text = text.split("(")[0].strip()
    else:
        main_text = text

    re.search("[0-9]+[ms]*\s*/\s*[0-9]+[ms]*", main_text)
    re.search("[a-z]+\s*[:,&\/]*\s*[0-9]+", main_text)
    re.search("[:,&\/]+", main_text)

    cleaned_text = clean_text(main_text)
    return cleaned_text


def get_stimuli_from_data(item: dict) -> List[StimulusFromData]:
    stimuli_from_data = []
    stimuli_categories = item["Stimuli Features.Categories"].split("+")
    stimuli_modalities = item["Stimuli Features.Modality"].split("+")
    stimuli_durations = str(item["Stimuli Features.Duration"]).split("+")

    if not len(stimuli_categories) == len(stimuli_modalities) == len(stimuli_durations):
        raise IncoherentStimuliDataError("not the same number of categories to modalities to durations")

    for category, modality, duration in zip(stimuli_categories, stimuli_modalities, stimuli_durations):
        # resolve category and sub-category (if existing)
        if (category == "") or (modality == ""):
            raise MissingValueInStimuliError("missing value for category of modality")
        if "(" not in category:
            resolved_category = category.strip()
            resolved_sub_category = None
        else:
            resolved_category = category.split("(")[0].strip()
            sub_category = category.split("(")[1].split(")")[0].strip()
            resolved_sub_category = clean_text(sub_category)

        clean_category = clean_text(resolved_category)

        # resolve modality
        modality_type = clean_text(modality.strip())
        resolved_modality = ""
        for modality_name in modalities:
            if modality_type.lower() == modality_name.lower():
                resolved_modality = modality_name
            else:
                continue

        # resolve duration
        none_values = ["N/A", "NA", "N.A", "None", "0", 0, "none", ""]
        clean_duration = clean_duration_text(duration)
        resolved_duration = None
        try:
            if "ms" in clean_duration:
                raw_duration = clean_duration.split("ms")[0]
                duration_ms = float(raw_duration.strip().split(" ")[-1].strip())
            elif "sec" in clean_duration:
                raw_duration = clean_duration.split("sec")[0].strip()
                duration_ms = int(raw_duration.strip().split(" ")[-1].strip()) * 1000
            elif clean_duration in none_values:
                duration_ms = None
            else:
                raise StimulusDurationError(f"unable to process duration data: {clean_duration}")
            resolved_duration = str(duration_ms)

        except ValueError as error:
            logger.exception(f"{error} while processing stimuli duration data")
            raise StimulusDurationError()

        stimuli_from_data.append(
            StimulusFromData(
                category=clean_category,
                sub_category=resolved_sub_category,
                modality=resolved_modality,
                duration=resolved_duration,
            )
        )
    return stimuli_from_data


def get_sample_from_data(item: dict) -> List[SampleFromData]:
    samples = []
    sample_type_data = str(item["Sample.Type"]).split("+")
    total_sample_data = str(item["Sample.Total"]).split("+")
    included_sample_data = str(item["Sample.Included"]).split("+")
    notes = []

    if not len(sample_type_data) == len(total_sample_data) == len(included_sample_data):
        if sample_type_data[0] in ["6", 6]:
            pass
        else:
            raise IncoherentSampleDataError()

    for sample_type, total_sample, included_sample in zip(sample_type_data, total_sample_data, included_sample_data):
        # resolve for sample type
        if "(" in sample_type:
            sample_type_number = str(sample_type).split("(")[0].strip()
            sample_type_notes = sample_type.split("(")[1].split(")")[0]
            note = add_to_notes("sample type", sample_type_notes)
            notes.append(note)
        else:
            sample_type_number = str(sample_type).strip()

        if sample_type_number == "0":
            resolved_sample_type = SampleChoices.HEALTHY_ADULTS
        elif sample_type_number == "1":
            resolved_sample_type = SampleChoices.HEALTHY_COLLEGE_STUDENTS
        elif sample_type_number == "2":
            resolved_sample_type = SampleChoices.CHILDREN
        elif sample_type_number == "3":
            resolved_sample_type = SampleChoices.PATIENTS
        elif sample_type_number == "5":
            resolved_sample_type = SampleChoices.NON_HUMAN
        elif sample_type_number == "6":
            resolved_sample_type = SampleChoices.COMPUTER
        elif sample_type_number == "7":
            resolved_sample_type = SampleChoices.YOUNG_PATIENTS
        else:
            raise SampleTypeError()

        # resolve for total sample size
        if resolved_sample_type == SampleChoices.COMPUTER:
            resolved_total_sample = 0
            resolved_included_sample = 0
        else:
            if "(" in total_sample:
                resolved_total_sample = total_sample.split("(")[0].strip()
                sample_total_notes = total_sample.split("(")[1].split(")")[0]
                note = add_to_notes("sample total", sample_total_notes)
                notes.append(note)
            else:
                resolved_total_sample = total_sample.strip()

            # resolve for included sample size
            if "(" in included_sample:
                resolved_included_sample = included_sample.split("(")[0].strip()
                included_sample_notes = included_sample.split("(")[1].split(")")[0]
                note = add_to_notes("sample included", included_sample_notes)
                notes.append(note)
            else:
                resolved_included_sample = included_sample.strip()

        notes_string = "; ".join(map(str, notes))
        sample = SampleFromData(
            sample_type=resolved_sample_type,
            total_size=resolved_total_sample,
            included_size=resolved_included_sample,
            note=notes_string,
        )
        samples.append(sample)

    return samples
