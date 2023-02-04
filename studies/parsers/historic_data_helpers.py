from configuration.initial_setup import finding_tags_map
from studies.models import Paradigm


def get_paradigms_from_data(paradigms: dict, item: dict) -> list:
    paradigms_in_data = []
    parent = Paradigm()

    for paradigm in paradigms["parent_paradigms"]:
        if paradigm not in item["Experimental paradigms.Main Paradigm"]:
            continue
        parent = Paradigm.objects.get_or_create(name=paradigm)
        paradigms_in_data.append(parent)

    if "Motoric" in item["Experimental paradigms.Specific Paradigm"]:
        imagination = Paradigm.objects.get(name='Imagination')
        parsed_paradigm = Paradigm.objects.get_or_create(name="Motoric", parent=imagination)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Abnormal_Contents_of_Consciousness"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        abnormal_contents_of_consciousness = Paradigm.objects.get(name='Abnormal Contents of Consciousness')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=abnormal_contents_of_consciousness)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Anesthesia"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        anesthesia = Paradigm.objects.get(name='Anesthesia')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=anesthesia)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Attentional_Manipulation"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        attentional_manipulation = Paradigm.objects.get(name='Attentional Manipulation')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=attentional_manipulation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Case_Study"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        case_study = Paradigm.objects.get(name='Case Study')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=case_study)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Cognitive_Tasks"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        cognitive_tasks = Paradigm.objects.get(name='Cognitive Tasks')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=cognitive_tasks)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Competition_Binocular"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        competition_binocular = Paradigm.objects.get(name='Competition (Binocular)')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=competition_binocular)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Direct_Stimulation"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        direct_stimulation = Paradigm.objects.get(name='Direct Stimulation')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=direct_stimulation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Disorders_of_Consciousness"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        disorders_of_consciousness = Paradigm.objects.get(name='Disorders of Consciousness')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=disorders_of_consciousness)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Emotional",
                     "Oddball",
                     "Prior Exposure"]:
        if paradigm not in item["Expectation"]:
            continue
        expectation = Paradigm.objects.get(name='Expectation')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=expectation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Own Name",
                     "Prior Exposure (Familiarity)",
                     "Self-Face"]:
        if paradigm not in item["Familiarity"]:
            continue
        familiarity = Paradigm.objects.get(name='Familiarity')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=familiarity)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Illusions"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        illusions = Paradigm.objects.get(name='Illusions')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=illusions)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Masking"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        masking = Paradigm.objects.get(name='Masking')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=masking)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Ketamine (Psychedelic Drugs)",
                     "Psilocybin"]:
        psychedelic_drugs = Paradigm.objects.get(name='Psychedelic Drugs')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=psychedelic_drugs)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in paradigms["Sedation"]:
        if paradigm not in item["Experimental paradigms.Specific Paradigm"]:
            continue
        sedation = Paradigm.objects.get(name='Sedation')
        parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=sedation)
        paradigms_in_data.append(parsed_paradigm)

    for paradigm in ["Brief Presentation",
                     "Coherence Reduction",
                     "Intensity Reduction",
                     "Noise Induction"]:
        if paradigm in item["Experimental paradigms.Specific Paradigm"]:
            stimulus_degradation = Paradigm.objects.get(name='Stimulus Degradation')
            parsed_paradigm = Paradigm.objects.get_or_create(name=paradigm, parent=stimulus_degradation)
            paradigms_in_data.append(parsed_paradigm)

    return paradigms_in_data




