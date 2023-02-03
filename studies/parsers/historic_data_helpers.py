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


def get_finding_description_from_data(item):
    findings_ncc_tags = item["Findings.NCC Tags [0 = Frontal, 1= Ventral Stream, 2 = V1, 3 = P300, 4= VAN, 5= Gamma, " \
                             "6= Complexity, 7=Local Synchronization, 8= Global Synchronization, 9 = Fronto Parietal " \
                             "connectivity, 10 = Variability, 11 = A1, 12 = Dorsal Stream, 13 = Beta, 14 = Alpha, " \
                             "15 = CNV, 16 = Parietal, 17 = DMN, 18 = Small Worldness, 19 = PHI Approximation, " \
                             "20 = Metacognition, 21 = Posterior, 22 = N2pc, 23 = Recurrent Processing, " \
                             "24 = GABA/NMDA, 25 = P2, 26 = MMN, 27 = N2, 28 = Theta, 29 = Delta , 30 = ART, 31 = V4, " \
                             "32 = Early Components, 33 = Late Components, 34 = Temporal Parietal Connectivity, " \
                             "35 = S1, 36 = N140, 37 = N170, 38 = Centrality, 39 = N1, 40 = CFC, 41 = Anterior " \
                             "Posterior Connectivity, 42 = Subcortical structures, 43 = Cortical Subcortical " \
                             "connectivity, 44 = Acetylcholine, 46 = SN, 47 = Motor areas connectivity, 48 = Temporal " \
                             "Occipital connectivity, 49 = Prestimulus Components, 50 = Low frequencies <1Hz, " \
                             "51 = Uncinate Fasciculus, 53 = SPCN, 55 = Figure Ground Difference, 56 = Border " \
                             "Difference, 57 = P1, 58 = Frequency Increase,59 = Sleep Spindles,  60 = Slow Waves " \
                             "Activity, 62 = ERN, 63 = EPN, 64 = Hyper Synchronization, 65 = Plasticity, " \
                             "66 = Anatomic Functional connectivity similarity,67 = Ultra slow fluctuations, " \
                             "69 = M70, 70 = M130, 71 = ARN, 72 = M280, 74 = N400, 75 = Pe, 76 = Change related " \
                             "positivity, 77 = N150, 78 = Intermediate Components, 79 = SSVEP, 80 = inter lobe " \
                             "connectivity, 81 = Intrinsic Ignition, 82 = Ignition Variability, 83 = Hierarchical " \
                             "Structure, 84 = SCP, 85 = AAN, 86 = Dorsal Attention Network, 87 = Visual network]"]

    return findings_ncc_tags


def get_finding_tag_type_from_data(finding_tag_types: dict, item: dict) -> tuple:
    findings_ncc_tags = get_finding_description_from_data(item)

    finding_tag_type_in_data = ()
    for tag_type in finding_tag_types['Temporal']:
        if tag_type not in findings_ncc_tags:
            continue
        finding_tag_type_in_data = (tag_type, 'Temporal')

    for tag_type in finding_tag_types['Spatial_Areas']:
        if tag_type not in findings_ncc_tags:
            continue
        finding_tag_type_in_data = (tag_type, 'Spatial_Areas')

    for tag_type in finding_tag_types['miscellaneous']:
        if tag_type not in findings_ncc_tags:
            continue
        finding_tag_type_in_data = (tag_type, 'miscellaneous')

    return finding_tag_type_in_data
