from collections import namedtuple

from configuration.initial_setup import task_types_mapping, findings_measures
from studies.choices import TheoryDrivenChoices
from studies.models import Theory, Paradigm, MeasureType, Measure

SampleSizeFromData = namedtuple("SampleSizeFromData", ["total_size", "included_size"])


def get_sample_size_from_data(item):
    total_sample_data = item["Sample.Total"]
    if "(" in total_sample_data:
        total_samples = total_sample_data.split("(")
    included_sample_data = item["Sample.Included"]
    if "(" in included_sample_data:
        total_samples = included_sample_data.split("(")

    # sample_total_list = [sample.split("(")[0].strip() for sample in total_samples]

    # included_samples = item["Sample.Total"].split("(")[0]

    pass


def find_in_list(lookup_value: str, search_list: list):
    found_item = ""
    for item in search_list:
        if lookup_value.strip().lower() == item.lower():
            found_item = item
    return found_item


def parse_consciousness_measure_type_from_data(text: str):
    consciousness_measure_type_lookup = ["None",
                                         "Condition Assessment",
                                         "Subjective",
                                         "State Induction Assessment",
                                         "Sleep Monitoring",
                                         "Objective"]

    consciousness_measure_types = text.split("+")
    consciousness_measure_types_list = []
    for consciousness_measure_type in consciousness_measure_types:
        if "(" in consciousness_measure_type:
            resolved_type = find_in_list(consciousness_measure_type.split("(")[0], consciousness_measure_type_lookup)
        else:
            resolved_type = (find_in_list(consciousness_measure_type, consciousness_measure_type_lookup))
        consciousness_measure_types_list.append(resolved_type)

    return consciousness_measure_types_list


def parse_consciousness_measure_phases_from_data(text: str):
    consciousness_measure_phase_lookup = ["None",
                                          "Post Experiment",
                                          "Pre Experiment",
                                          "Separate Experiment",
                                          "Trial By Trial"]

    consciousness_measure_phases = text.split("+")
    consciousness_measure_phases_list = []
    for consciousness_measure_phase in consciousness_measure_phases:
        if "(" in consciousness_measure_phase:
            resolved_phase = find_in_list(consciousness_measure_phase.split("(")[0], consciousness_measure_phase_lookup)
        else:
            resolved_phase = (find_in_list(consciousness_measure_phase, consciousness_measure_phase_lookup))
        consciousness_measure_phases_list.append(resolved_phase)

    return consciousness_measure_phases_list


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
    # parent = Paradigm()
    parsed_main_paradigms = item["Experimental paradigms.Main Paradigm"].split(" + ")
    parsed_paradigms = item["Experimental paradigms.Specific Paradigm"].split(" + ")
    specific_paradigms = [paradigm.split("(")[0].strip() for paradigm in parsed_paradigms]

    for paradigm in paradigms["parent_paradigms"]:
        if paradigm not in parsed_main_paradigms:
            continue
        parent = Paradigm.objects.get_or_create(name=paradigm)
        paradigms_in_data.append(parent)

    if "Motoric" in specific_paradigms:
        imagination = Paradigm.objects.get(name='Imagination')
        parsed_paradigm = Paradigm.objects.get_or_create(name="Motoric", parent=imagination)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Abnormal_Contents_of_Consciousness"]:
        if paradigm not in specific_paradigms:
            continue
        abnormal_contents_of_consciousness = Paradigm.objects.get(name='Abnormal Contents of Consciousness')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=abnormal_contents_of_consciousness)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Anesthesia"]:
        if paradigm not in specific_paradigms:
            continue
        anesthesia = Paradigm.objects.get(name='Anesthesia')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=anesthesia)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Attentional_Manipulation"]:
        if paradigm not in specific_paradigms:
            continue
        attentional_manipulation = Paradigm.objects.get(name='Attentional Manipulation')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=attentional_manipulation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Case_Study"]:
        if paradigm not in specific_paradigms:
            continue
        case_study = Paradigm.objects.get(name='Case Study')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=case_study)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Cognitive_Tasks"]:
        if paradigm not in specific_paradigms:
            continue
        cognitive_tasks = Paradigm.objects.get(name='Cognitive Tasks')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=cognitive_tasks)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Competition_Binocular"]:
        if paradigm not in specific_paradigms:
            continue
        competition_binocular = Paradigm.objects.get(name='Competition (Binocular)')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=competition_binocular)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Direct_Stimulation"]:
        if paradigm not in specific_paradigms:
            continue
        direct_stimulation = Paradigm.objects.get(name='Direct Stimulation')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=direct_stimulation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Disorders_of_Consciousness"]:
        if paradigm not in specific_paradigms:
            continue
        disorders_of_consciousness = Paradigm.objects.get(name='Disorders of Consciousness')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=disorders_of_consciousness)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Emotional",
                     "Oddball",
                     "Prior Exposure"]:
        if paradigm not in specific_paradigms:
            continue
        expectation = Paradigm.objects.get(name='Expectation')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=expectation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Own Name",
                     "Prior Exposure (Familiarity)",
                     "Self-Face"]:
        if paradigm not in specific_paradigms:
            continue
        familiarity = Paradigm.objects.get(name='Familiarity')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=familiarity)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Illusions"]:
        if paradigm not in specific_paradigms:
            continue
        illusions = Paradigm.objects.get(name='Illusions')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=illusions)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Masking"]:
        if paradigm not in specific_paradigms:
            continue
        masking = Paradigm.objects.get(name='Masking')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=masking)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Ketamine (Psychedelic Drugs)",
                     "Psilocybin"]:
        if paradigm not in specific_paradigms:
            continue
        psychedelic_drugs = Paradigm.objects.get(name='Psychedelic Drugs')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=psychedelic_drugs)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Sedation"]:
        if paradigm not in specific_paradigms:
            continue
        sedation = Paradigm.objects.get(name='Sedation')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=sedation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Brief Presentation",
                     "Coherence Reduction",
                     "Intensity Reduction",
                     "Noise Induction"]:
        if paradigm in specific_paradigms:
            stimulus_degradation = Paradigm.objects.get(name='Stimulus Degradation')
            parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=stimulus_degradation)
            paradigms_in_data.append(parsed_paradigm)

    return paradigms_in_data


MeasureFromData = namedtuple("MeasureFromData", ["measure_type", "measure_notes"])


def get_measures_from_data(item: dict):
    measures_data = item['Findings.Measures [0 = Decoding, 1 = BOLD, 2 = Frequencies, 3= ERP, 4 = Mutual Information,' \
                         '5 = Synchronization, 6 = Behavioral (Accuracy), 7 = Behavioral (RT), 9 = Connectivity, ' \
                         '10 = PHI, 11 = Graph theoretical measures, 14 = Entropy, 15 = Global Field Power, 16 = PCA, ' \
                         '17 = Lempel Ziv, 18 = H2_15O, 19 = Variability, 20 = Adaptation, 21 = Metacognition, ' \
                         '22 = Visibility, 25 = Dimension of activation, 26 = fALFF, 27 = 18F Fluorodeoxyglucose, ' \
                         '28 = CFC , 29 = LRTC, 30 = Calcium Imaging, 31 = K Complex, 32 = TCT, 33 = DISS, ' \
                         '34 = Observation, 35 = Microstates, 36 = Stimulation Reactivity, 37 = Frequency Tagging, ' \
                         '39 = Hopf bifurcation parameter, 41 = Slow Wave Activity, 42 = Auto Information Flow, ' \
                         '43 = Cross Information Flow ciF, 44 = Auto Correlation, 45 = Topo, 46 = PCI, ' \
                         '47 = Physiological Measure, 49 = Computer Simulations, 50 = Phosphene Threshold, ' \
                         '51 = Frequency Change Index, 52 = Brain Behavior Correlation, 56 = Nonlinear correlation index, ' \
                         '57 =DSI, 58 = Complexity of functional connectivity, 63 = BIS, 64 = Correlation dimension, ' \
                         '65 = Dominance, 66 = Epileptogenicity Index, 67 = Spike Suppression, 68 = Mean Dwell Time, ' \
                         '69 = Network Backbones, 70 = SSVEP, 71= Fractal Dimension]']
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


StimulusFromData = namedtuple("StimulusFromData", ["category", "sub_category", "modality", "duration"])


def get_stimuli_from_data(item):
    stimuli_from_data = []
    stimuli_categories = item["Stimuli Features.Categories"].split("+")
    stimuli_modalities = item["Stimuli Features.Modality"].split("+")
    stimuli_durations = item["Stimuli Features.Duration"].split("+")
    if not len(stimuli_categories) == len(stimuli_modalities) == len(stimuli_durations):
        raise ProblemInExistingDataException
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
        for modality in ["Auditory",
                         "None",
                         "Olfactory",
                         "Tactile",
                         "Visual"]:
            if modality_type == modality:
                resolved_modality = modality_type
        # resolve duration
        stimulus_duration = duration
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
        else:
            duration_ms = 0
        duration_micros = int(duration_ms * 1000)
        resolved_duration = duration_ms # TODO: change to duration_micros if needed

        stimuli_from_data.append(StimulusFromData(category=resolved_category, sub_category=sub_category,
                                                  modality=resolved_modality, duration=resolved_duration))
    return stimuli_from_data


class ProblemInExistingDataException(Exception):
    pass