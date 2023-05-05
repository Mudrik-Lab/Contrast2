import json
import unittest
from typing import Any

from configuration.initial_setup import consciousness_measure_types
from studies.parsers.historic_data_helpers import find_in_list, get_paradigms_from_data
from studies.parsers.parsing_findings_Contrast2 import parse
from studies.parsers.process_row import process_row, create_study
from studies.parsers.studies_parsing_helpers import parse_authors_from_authors_text, \
    resolve_country_from_affiliation_text
from contrast_api.tests.base import BaseTestCase
from studies.tests.implementation_tests.test_study_parsers_helpers import test_data_doesnt_exist


class StudyParserHelpersTestCase(BaseTestCase):
    def test_parsing_authors_from_affiliation_text(self):
        text = 'Zhou S., Zou G., Xu J., Su Z., Zhu H., Zou Q., Gao J.-H.'
        res = parse_authors_from_authors_text(text)
        self.assertEqual(res, ['Zhou S.', 'Zou G.', 'Xu J.', 'Su Z.', 'Zhu H.', 'Zou Q.', 'Gao J.-H.'])

    # TODO: somewhere we need to make sure names don't include ", " so they don't break

    def test_resolving_countries_from_affiliation_text(self):
        text = 'Department of Physiology and Pharmacology, Sackler School of Medicine, Tel Aviv University, Tel Aviv, 6997801, Israel; Department of Anesthesiology and Critical Care Medicine, Hadassah-Hebrew University Medical Center, Jerusalem, 91120, Israel; Hadassah School of Medicine, Hebrew University, Jerusalem, 91120, Israel; Sagol School of Neuroscience, Tel Aviv University, Tel Aviv, 6997801, Israel; Functional Neurosurgery Unit, Tel Aviv Sourasky Medical Center, Tel Aviv, 6423906, Israel; Department of Neurology and Neurosurgery, Sackler School of Medicine, Tel Aviv University, Tel Aviv, 6997801, Israel; Department of Anesthesia, Intensive Care and Pain, Tel Aviv Medical Center, Sackler Medical School, Tel Aviv University, Tel Aviv, 6997801, Israel; EEG and Epilepsy Unit, Department of Neurology, Tel Aviv Sourasky Medical Center, Tel Aviv, 6423906, Israel; Department of Anesthesiology and Intensive Care Medicine, University of Bonn Medical Center, Bonn, 53127, Germany; Department of Neurosurgery, University of Bonn Medical Center, Bonn, 53127, Germany; Department of Epileptology, University of Bonn Medical Center, Bonn, 53127, Germany; Department of Neurosurgery, University of California, Los Angeles, CA  90095, United States'
        res = resolve_country_from_affiliation_text(text)
        self.assertEqual(res, {"United States", "Israel", "Germany"})

    def test_getting_resolved_list_from_data(self):
        consciousness_measure_type_lookup = consciousness_measure_types
        text1 = "Objective + Subjective (Confidence)"
        text2 = "Sleep Monitoring + State Induction Assessment"
        text3 = "Subjective + Objective"
        lookup_list1 = text1.split("+")
        lookup_list2 = text2.split("+")
        lookup_list3 = text3.split("+")
        res1 = find_in_list(lookup_list1, consciousness_measure_type_lookup)
        res2 = find_in_list(lookup_list2, consciousness_measure_type_lookup)
        res3 = find_in_list(lookup_list3, consciousness_measure_type_lookup)

        self.assertEqual(len(res1), 2)
        self.assertEqual(res1[0], "Objective")
        self.assertEqual(res3[1], "Objective")
        self.assertEqual(len(res3), 2)

    def test_finding_tag_parser(self):
        text = "50 (# The findings of frontal and posterior areas are reflecting significant differences between light" \
               " and deep sedation states in this measure) + 0 (medial PFC & Orbital PFC & dorsolateral PFC & Insular" \
               " Cortex &) + 21 (Temporal Pole &) + 8 (#frequency analysis of slow oscillations considered to reflect" \
               " long distance synchronization) + 42 (Amygdala & Hippocampus & Parahippocampal Gyrus)"
        res = parse(text)
        self.assertEqual(len(res), 10)

        text2 = "41(connectivity between A1 and ACC ) + 11 + 16 (posterior cingulate cortex# −5 −49 26)"
        res = parse(text2)
        self.assertEqual(len(res), 3)

        text3 = "5 (Connectivity 90-120Hz) + 7 (?) + 8 (Normalized Degree) + 6 (Dimension of activation) + 14 (Connectivity Neg 7-13Hz) + 38 (Normalized Degree)"
        res = parse(text3)
        self.assertEqual(len(res), 6)

        text4 = "-5 (Power 30-40Hz<340-420ms> # gamma activity reflected task relevance and not visibility)+ -3(380-550ms # P300 reflected task relevance and not visibility)"
        res = parse(text4)
        self.assertEqual(len(res), 2)

    def given_studies_exist(self, test_studies: list) -> list:
        studies_data = []
        for study_item in test_studies:
            try:
                study = create_study(item=study_item)
                studies_data.append(study)
            except:
                print(json.dumps(study_item))
                raise AssertionError()

        return studies_data

    def test_paradigm_parser(self):
        item_monocular = {"Experimental paradigms.Main Paradigm": "Competition (Monocular)",
                          "Experimental paradigms.Specific Paradigm": "Bistable percepts (Competition (Monocular))"}
        res = get_paradigms_from_data(item_monocular)
        self.assertEqual(len(res), 2)

        item_sedation = {"Experimental paradigms.Main Paradigm": "Sedation + Resting State",
                         "Experimental paradigms.Specific Paradigm": "Medetomidine (Sedation)"}

        res = get_paradigms_from_data(item_sedation)
        self.assertEqual(len(res), 4)

        item_cueing = {"Experimental paradigms.Main Paradigm": "Contextual Cueing",
                       "Experimental paradigms.Specific Paradigm": ""}

        res = get_paradigms_from_data(item_cueing)
        self.assertEqual(len(res), 2)

        item_spinal_cord = {"Experimental paradigms.Main Paradigm": "Direct Stimulation + Disorders of Consciousness",
                            "Experimental paradigms.Specific Paradigm": "Spinal Cord Stimulation (Direct Stimulation, "
                                                                        "Spinal Cord) + Unresponsive Wakefulness Syndrome "
                                                                        "(Disorders of Consciousness) + Minimal Consciousness"
                                                                        " State (Disorders of Consciousness)"}

        res = get_paradigms_from_data(item_spinal_cord)
        print(res)
        self.assertEqual(len(res), 5)

        item_TMS = {"Experimental paradigms.Main Paradigm": "Direct Stimulation + Masking",
                    "Experimental paradigms.Specific Paradigm": "TMS (Direct Stimulation, early visual cortex)"
                                                                " + Backward Masking (Masking)"}

        res = get_paradigms_from_data(item_TMS)
        self.assertEqual(len(res), 4)

