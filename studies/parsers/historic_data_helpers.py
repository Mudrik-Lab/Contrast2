import re
from collections import namedtuple
from itertools import zip_longest, chain

from configuration.initial_setup import task_types_mapping, findings_measures
from studies.choices import TheoryDrivenChoices, SampleChoices
from studies.models import Theory, Paradigm, Stimulus


class ProblemInTheoryDrivenExistingDataException(Exception):
    pass


class ProblemInStimuliExistingDataException(Exception):
    pass


class ProblemInSampleExistingDataException(Exception):
    pass


ConsciousnessMeasureFromData = namedtuple("ConsciousnessMeasureFromData", ["type", "phase"])
ParadigmFromData = namedtuple("ParadigmFromData", ["parent", "name"])
MeasureFromData = namedtuple("MeasureFromData", ["measure_type", "measure_notes"])
StimulusFromData = namedtuple("StimulusFromData", ["category", "sub_category", "modality", "duration"])
SampleFromData = namedtuple("SampleFromData", ["sample_type", "total_size", "included_size", "note"])


def add_to_notes(prefix, text: str):
    note = f'{prefix} notes: {text}; '
    return note


def get_sample_from_data(item):
    sample_type_data = item["Sample.Type"].split("+")
    total_sample_data = item["Sample.Total"]
    included_sample_data = item["Sample.Included"]
    notes = []

    if len(sample_type_data) == 1:
        sample_type = sample_type_data[0]
        if "(" in sample_type:
            sample_type_number = sample_type.split("(")[0].strip()
            sample_type_notes = sample_type.split("(")[1].split(")")[0]
            note = add_to_notes("sample type", sample_type_notes)
            notes.append(note)
        else:
            sample_type_number = sample_type.strip()

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
        else:
            raise ProblemInSampleExistingDataException

        if "(" in total_sample_data:
            resolved_total_sample = total_sample_data.split("(")[0].strip()
            sample_total_notes = total_sample_data.split("(")[1].split(")")[0]
            note = add_to_notes("sample total", sample_total_notes)
            notes.append(note)
        else:
            resolved_total_sample = total_sample_data.strip()

        if "(" in included_sample_data:
            resolved_included_sample = included_sample_data.split("(")[0].strip()
            included_sample_notes = total_sample_data.split("(")[1].split(")")[0]
            note = add_to_notes("sample included", included_sample_notes)
            notes.append(note)
        else:
            resolved_included_sample = included_sample_data.strip()
        notes_string = chain.from_iterable(notes)
        sample = SampleFromData(sample_type=resolved_sample_type, total_size=resolved_total_sample,
                                included_size=resolved_included_sample, note=notes_string)
    else:
        raise ProblemInSampleExistingDataException()

    return sample


def find_in_list(lookup_list: list, search_list: list):
    resolved_list = [[item for item in search_list if lookup_value.split("(")[0].strip().lower() == item.lower()]
                     if "(" in lookup_value
                     else [item for item in search_list if lookup_value.strip().lower() == item.lower()]
                     for lookup_value in lookup_list]

    return resolved_list


def get_consciousness_measure_type_and_phase_from_data(item):
    cm_phase_list = item['Measures of consciousness.Type'].split("+")
    cm_type_list = item['Measures of consciousness.Measures Taken'].split("+")
    consciousness_measure_phase_lookup = ["None",
                                          "Post Experiment",
                                          "Pre Experiment",
                                          "Separate Experiment",
                                          "Trial By Trial"]
    consciousness_measure_type_lookup = ["None",
                                         "Condition Assessment",
                                         "Subjective",
                                         "State Induction Assessment",
                                         "Sleep Monitoring",
                                         "Objective"]
    results = []
    resolved_phases = [[item for item in consciousness_measure_phase_lookup if
                        lookup_value.split("(")[0].strip().lower() == item.lower()]
                       if "(" in lookup_value
                       else [item for item in consciousness_measure_phase_lookup if
                             lookup_value.strip().lower() == item.lower()]
                       for lookup_value in cm_phase_list]

    resolved_types = [[item for item in consciousness_measure_type_lookup if
                       lookup_value.split("(")[0].strip().lower() == item.lower()]
                      if "(" in lookup_value
                      else [item for item in consciousness_measure_type_lookup if
                            lookup_value.strip().lower() == item.lower()]
                      for lookup_value in cm_type_list]

    phases = chain.from_iterable(resolved_phases)
    types = chain.from_iterable(resolved_types)

    for resolved_phase, resolved_type in zip_longest(phases, types):
        if resolved_phase and resolved_type:
            results.append(ConsciousnessMeasureFromData(type=resolved_type, phase=resolved_phase))
        elif resolved_phase and not resolved_type:
            results.append(ConsciousnessMeasureFromData(type=resolved_types[0], phase=resolved_phase))
        elif resolved_type and not resolved_phase:
            results.append(ConsciousnessMeasureFromData(type=resolved_type, phase=resolved_phases[0]))
        else:
            break

    return results


def parse_theory_driven_from_data(item: dict, theories: list) -> tuple:
    theory_driven = ""
    theory_driven_theories = []
    for key, value in item.items():
        if "Theory Driven" not in key:
            continue
        theory_driven_choice = value[0]
        if theory_driven_choice == "0":
            theory_driven = TheoryDrivenChoices.POST_HOC
        elif theory_driven_choice == "1":
            theory_driven = TheoryDrivenChoices.MENTIONING
            for theory in theories:
                if theory not in value:
                    continue
                theory = Theory.objects.get(name=theory)
                theory_driven_theories.append(theory)
        elif theory_driven_choice == "2":
            theory_driven = TheoryDrivenChoices.DRIVEN
            for theory in theories:
                if theory not in value:
                    continue
                theory = Theory.objects.get(name=theory)
                theory_driven_theories.append(theory)
        else:
            raise ProblemInTheoryDrivenExistingDataException()

    return theory_driven, theory_driven_theories


def parse_task_types(item: dict):
    parsed_task_types = []
    for key, value in item.items():
        if "Task.Code" not in key:
            continue
        tasks_codes_breakdown = value.split("+")
        for task_code in tasks_codes_breakdown:
            parsed_task_code = task_code.split("(")[0].strip()
            parsed_task = task_types_mapping[parsed_task_code]
            parsed_task_types.append(parsed_task)

    return parsed_task_types


def get_paradigms_from_data(paradigms: dict, item: dict) -> list:
    paradigms_in_data = []
    parsed_main_paradigms = item["Experimental paradigms.Main Paradigm"].split(" + ")
    parsed_paradigms = item["Experimental paradigms.Specific Paradigm"].split(" + ")
    specific_paradigms = [paradigm.split("(")[0].strip() for paradigm in parsed_paradigms]

    for paradigm in paradigms["parent_paradigms"]:
        if paradigm not in parsed_main_paradigms:
            continue
        parent = ParadigmFromData(name=paradigm, parent=None)
        paradigms_in_data.append(parent)

    if "Motoric" in specific_paradigms:
        imagination = Paradigm.objects.get(name='Imagination')
        parsed_paradigm = ParadigmFromData(name="Motoric", parent=imagination)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Abnormal_Contents_of_Consciousness"]:
        if paradigm not in specific_paradigms:
            continue
        abnormal_contents_of_consciousness = Paradigm.objects.get(name='Abnormal Contents of Consciousness')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=abnormal_contents_of_consciousness)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Anesthesia"]:
        if paradigm not in specific_paradigms:
            continue
        anesthesia = Paradigm.objects.get(name='Anesthesia')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=anesthesia)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Attentional_Manipulation"]:
        if paradigm not in specific_paradigms:
            continue
        attentional_manipulation = Paradigm.objects.get(name='Attentional Manipulation')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=attentional_manipulation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Case_Study"]:
        if paradigm not in specific_paradigms:
            continue
        case_study = Paradigm.objects.get(name='Case Study')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=case_study)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Cognitive_Tasks"]:
        if paradigm not in specific_paradigms:
            continue
        cognitive_tasks = Paradigm.objects.get(name='Cognitive Tasks')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=cognitive_tasks)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Competition_Binocular"]:
        if paradigm not in specific_paradigms:
            continue
        competition_binocular = Paradigm.objects.get(name='Competition (Binocular)')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=competition_binocular)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Direct_Stimulation"]:
        if paradigm not in specific_paradigms:
            continue
        direct_stimulation = Paradigm.objects.get(name='Direct Stimulation')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=direct_stimulation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Disorders_of_Consciousness"]:
        if paradigm not in specific_paradigms:
            continue
        disorders_of_consciousness = Paradigm.objects.get(name='Disorders of Consciousness')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=disorders_of_consciousness)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Emotional",
                     "Oddball",
                     "Prior Exposure"]:
        if paradigm not in specific_paradigms:
            continue
        expectation = Paradigm.objects.get(name='Expectation')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=expectation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Own Name",
                     "Prior Exposure (Familiarity)",
                     "Self-Face"]:
        if paradigm not in specific_paradigms:
            continue
        familiarity = Paradigm.objects.get(name='Familiarity')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=familiarity)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Illusions"]:
        if paradigm not in specific_paradigms:
            continue
        illusions = Paradigm.objects.get(name='Illusions')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=illusions)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Masking"]:
        if paradigm not in specific_paradigms:
            continue
        masking = Paradigm.objects.get(name='Masking')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=masking)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Ketamine (Psychedelic Drugs)",
                     "Psilocybin"]:
        if paradigm not in specific_paradigms:
            continue
        psychedelic_drugs = Paradigm.objects.get(name='Psychedelic Drugs')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=psychedelic_drugs)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Sedation"]:
        if paradigm not in specific_paradigms:
            continue
        sedation = Paradigm.objects.get(name='Sedation')
        parsed_paradigm = ParadigmFromData(name=paradigm, parent=sedation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Brief Presentation",
                     "Coherence Reduction",
                     "Intensity Reduction",
                     "Noise Induction"]:
        if paradigm in specific_paradigms:
            stimulus_degradation = Paradigm.objects.get(name='Stimulus Degradation')
            parsed_paradigm = ParadigmFromData(name=paradigm, parent=stimulus_degradation)
            paradigms_in_data.append(parsed_paradigm)

    return paradigms_in_data


def get_measures_from_data(item: dict):
    measures_data = ""
    for key, value in item.items():
        if 'Findings.Measures' not in key:
            continue
        measures_data = value
    measures_data_split = measures_data.split("+")
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


def clean_stimulus_text(text):
    if "(" in text:
        main_text = text.split("(")[0].strip()
    else:
        main_text = text

    multiple_entries = re.search("[0-9]+[ms]*\s*/\s*[0-9]+[ms]*", main_text)
    verbose = re.search("[a-z]+\s[0-9]+", main_text)

    if multiple_entries or verbose:
        raise ProblemInStimuliExistingDataException()
    else:
        return main_text


def get_stimuli_from_data(item):
    stimuli_from_data = []
    stimuli_categories = item["Stimuli Features.Categories"].split("+")
    stimuli_modalities = item["Stimuli Features.Modality"].split("+")
    stimuli_durations = item["Stimuli Features.Duration"].split("+")
    allowed_categories_by_modality = Stimulus.allowed_categories_by_modality

    if not len(stimuli_categories) == len(stimuli_modalities) == len(stimuli_durations):
        raise ProblemInStimuliExistingDataException()

    for category, modality, duration in zip(stimuli_categories, stimuli_modalities, stimuli_durations):
        # resolve category and sub-category (if existing)
        resolved_category = ""
        sub_category = ""
        if "(" not in category:
            resolved_category = category.strip()
            sub_category = None
        else:
            resolved_category = category.split("(")[0].strip
            sub_category = category.split("(")[1].split(")")[0].strip()

        # resolve modality
        modality_type = modality.strip()
        resolved_modality = ""
        for modality_name in ["Auditory",
                              "None",
                              "Olfactory",
                              "Tactile",
                              "Visual"]:
            if modality_type == modality_name:
                resolved_modality = modality_type

        # check for fit between modality and category
        if resolved_category not in allowed_categories_by_modality[resolved_modality]:
            raise ProblemInStimuliExistingDataException()

        # resolve duration
        full_text_stimulus_duration = duration
        stimulus_duration = clean_stimulus_text(full_text_stimulus_duration)

        if "minute" in stimulus_duration:
            raw_duration = stimulus_duration.split("minute")[0].strip
            duration_ms = int(raw_duration) * 60000
        elif "ms" in stimulus_duration:
            raw_duration = stimulus_duration.split("ms")[0]
            duration_ms = float(raw_duration.strip().split(" ")[-1].strip())
        elif "micro" in stimulus_duration:
            raw_duration = stimulus_duration.split("micro")[0].strip
            duration_ms = float(raw_duration) / 1000
        elif "sec" in stimulus_duration:
            raw_duration = stimulus_duration.split("sec")[0].strip
            duration_ms = int(raw_duration.strip().split(" ")[-1].strip()) * 1000
        elif stimulus_duration == "N/A" or stimulus_duration == "NA" or stimulus_duration == "N.A" or \
                stimulus_duration == "None" or stimulus_duration == "0":
            duration_ms = None
        else:
            raise ProblemInStimuliExistingDataException()

        duration_micros = int(duration_ms * 1000)
        resolved_duration = str(duration_ms)  # TODO: change to duration_micros if needed

        stimuli_from_data.append(StimulusFromData(category=resolved_category, sub_category=sub_category,
                                                  modality=resolved_modality, duration=resolved_duration))
    return stimuli_from_data
