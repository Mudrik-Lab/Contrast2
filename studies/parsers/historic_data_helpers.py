from configuration.initial_setup import finding_tags_map
from studies.models import Paradigm


def get_paradigms_from_data(paradigms: dict, item: dict) -> list:
    paradigms_in_data = []
    parent = Paradigm()
    for paradigm in paradigms["parent_paradigms"]:
        if paradigm not in item["Experimental paradigms.Main Paradigm"]:
            continue
        parent = Paradigm.objects.get_or_create(name=paradigm)

    for paradigm in paradigms["Abnormal_Contents_of_Consciousness"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=parent)
        paradigms_in_data.append(parsed_paradigm)
    for paradigm in paradigms["Anesthesia"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=parent)
        paradigms_in_data.append(parsed_paradigm)
    for paradigm in paradigms["Attentional_Manipulation"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=parent)
        paradigms_in_data.append(parsed_paradigm)
    for paradigm in paradigms["Case_Study"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=parent)
        paradigms_in_data.append(parsed_paradigm)
    for paradigm in paradigms["Cognitive_Tasks"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=parent)
        paradigms_in_data.append(parsed_paradigm)
    for paradigm in paradigms["Competition_Binocular"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=parent)
        paradigms_in_data.append(parsed_paradigm)
    for paradigm in paradigms["Direct_Stimulation"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=parent)
        paradigms_in_data.append(parsed_paradigm)
    for paradigm in paradigms["Disorders_of_Consciousness"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=parent)
        paradigms_in_data.append(parsed_paradigm)
    for paradigm in paradigms["Illusions"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=parent)
        paradigms_in_data.append(parsed_paradigm)
    for paradigm in paradigms["Masking"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=parent)
        paradigms_in_data.append(parsed_paradigm)
    for paradigm in paradigms["Sedation"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=parent)
        paradigms_in_data.append(parsed_paradigm)

    return paradigms_in_data




