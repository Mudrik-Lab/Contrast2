from collections import namedtuple

from configuration.initial_setup import task_types_mapping
from studies.choices import TheoryDrivenChoices
from studies.models import Theory, Paradigm


SampleSizeFromData = namedtuple("SampleSizeFromData", ["total_size", "included_size"])


def get_sample_size_from_data(item):
    total_samples = item["Sample.Total"].split("(")[0]
    sample_total_list = [sample.split("(")[0].strip() for sample in total_samples]
    included_samples = item["Sample.Total"].split("(")[0]

    pass


def find_in_list(lookup_value: str, search_list: list):
    found_item = ""
    for item in search_list:
        if lookup_value.strip().lower() == item.lower():
            found_item = item
    return found_item


TypeFromData = namedtuple("TypeFromData", ["input_type", "input_comment"])


# TODO: change return type to list of dicts instead of tuples
def parse_consciousness_measure_type_from_data(text: str):
    ITEM_SEP = '+'
    START_FINDING_SEP = '('
    END_FINDING_SEP = ')'
    LOOKUP_LIST = ["None",
                   "Condition Assessment",
                   "Subjective",
                   "State Induction Assessment",
                   "Sleep Monitoring",
                   "Objective"]

    consciousness_measure_types = text.split(ITEM_SEP)
    consciousness_measure_types_list = []
    for consciousness_measure_type in consciousness_measure_types:
        if START_FINDING_SEP in consciousness_measure_type:
            resolved_type = find_in_list(consciousness_measure_type.split(START_FINDING_SEP)[0], LOOKUP_LIST)
            comment = consciousness_measure_type.split(START_FINDING_SEP)[1].replace(END_FINDING_SEP, '').strip()
        else:
            comment = ''
            resolved_type = (find_in_list(consciousness_measure_type, LOOKUP_LIST))
        type_from_data = TypeFromData(resolved_type, comment)
        consciousness_measure_types_list.append(type_from_data)

    return consciousness_measure_types_list


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
    parent_paradigms = item["Experimental paradigms.Main Paradigm"].split(" + ")
    parsed_paradigms = item["Experimental paradigms.Specific Paradigm"].split(" + ")
    specific_paradigms = [paradigm.split("(")[0].strip() for paradigm in parsed_paradigms]

    for paradigm in paradigms["parent_paradigms"]:
        if paradigm not in parent_paradigms:
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




