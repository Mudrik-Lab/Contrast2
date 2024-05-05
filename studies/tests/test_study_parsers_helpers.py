from configuration.initial_setup import consciousness_measure_types
from studies.parsers.historic_data_helpers import get_paradigms_from_data
from contrast_api.data_migration_functionality.helpers import find_in_list
from studies.parsers.parsing_findings_Contrast2 import parse
from contrast_api.data_migration_functionality.studies_parsing_helpers import (
    resolve_authors_from_authors_text,
    resolve_country_from_affiliation_text,
)
from contrast_api.tests.base import BaseTestCase


class StudyParserHelpersTestCase(BaseTestCase):
    def test_parsing_authors_from_affiliation_text(self):
        text = "Zhou S., Zou G., Xu J., Su Z., Zhu H., Zou Q., Gao J.-H."
        res = resolve_authors_from_authors_text(text)
        self.assertEqual(res, ["Zhou S.", "Zou G.", "Xu J.", "Su Z.", "Zhu H.", "Zou Q.", "Gao J.-H."])

    def test_resolving_countries_from_affiliation_text(self):
        text = "Department of Physiology and Pharmacology, Sackler School of Medicine, Tel Aviv University, Tel Aviv, 6997801, Israel; Department of Anesthesiology and Critical Care Medicine, Hadassah-Hebrew University Medical Center, Jerusalem, 91120, Israel; Hadassah School of Medicine, Hebrew University, Jerusalem, 91120, Israel; Sagol School of Neuroscience, Tel Aviv University, Tel Aviv, 6997801, Israel; Functional Neurosurgery Unit, Tel Aviv Sourasky Medical Center, Tel Aviv, 6423906, Israel; Department of Neurology and Neurosurgery, Sackler School of Medicine, Tel Aviv University, Tel Aviv, 6997801, Israel; Department of Anesthesia, Intensive Care and Pain, Tel Aviv Medical Center, Sackler Medical School, Tel Aviv University, Tel Aviv, 6997801, Israel; EEG and Epilepsy Unit, Department of Neurology, Tel Aviv Sourasky Medical Center, Tel Aviv, 6423906, Israel; Department of Anesthesiology and Intensive Care Medicine, University of Bonn Medical Center, Bonn, 53127, Germany; Department of Neurosurgery, University of Bonn Medical Center, Bonn, 53127, Germany; Department of Epileptology, University of Bonn Medical Center, Bonn, 53127, Germany; Department of Neurosurgery, University of California, Los Angeles, CA  90095, United States"
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
        find_in_list(lookup_list2, consciousness_measure_type_lookup)
        res3 = find_in_list(lookup_list3, consciousness_measure_type_lookup)

        self.assertEqual(len(res1), 2)
        self.assertEqual(res1[0], "Objective")
        self.assertEqual(res3[1], "Objective")
        self.assertEqual(len(res3), 2)

    def test_finding_tag_parser(self):
        text = (
            "50 (# The findings of frontal and posterior areas are reflecting significant differences between light"
            " and deep sedation states in this measure) + 0 (medial PFC & Orbital PFC & dorsolateral PFC & Insular"
            " Cortex &) + 21 (Temporal Pole &) + 8 (#frequency analysis of slow oscillations considered to reflect"
            " long distance synchronization) + 42 (Amygdala & Hippocampus & Parahippocampal Gyrus)"
        )
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

    def test_paradigm_parser_for_one_paradigm(self):
        item_monocular = {
            "Experimental paradigms.Main Paradigm": "Competition (Monocular)",
            "Experimental paradigms.Specific Paradigm": "Bistable percepts (Competition (Monocular))",
        }
        res = get_paradigms_from_data(item_monocular)
        # print(res)
        self.assertEqual(len(res), 2)

    def test_paradigm_competition(self):
        item_monocular = {
            "Experimental paradigms.Main Paradigm": "Competition (Binocular)",
            "Experimental paradigms.Specific Paradigm": "Binocular Rivalry (Competition (Binocular))",
        }
        res = get_paradigms_from_data(item_monocular)
        # print(res)
        self.assertEqual(len(res), 2)

    def test_paradigm_psilocybin(self):
        item_monocular = {
            "Experimental paradigms.Main Paradigm": "Psychedelic Drugs + Resting State",
            "Experimental paradigms.Specific Paradigm": "Psilocybin (Psychedelic Drugs)",
        }
        res = get_paradigms_from_data(item_monocular)
        # print(res)
        self.assertEqual(len(res), 4)

    def test_paradigm_direct_stimulation(self):
        item_monocular = {
            "Experimental paradigms.Main Paradigm": "Direct Stimulation + Disorders of Consciousness",
            "Experimental paradigms.Specific Paradigm": "tDCS (Direct Stimulation, lDLPFC) + Unresponsive "
            "Wakefulness Syndrome (Disorders of Consciousness) + "
            "Minimal Consciousness State (Disorders of Consciousness)"
            " + Emergence from MCS (Disorders of Consciousness)",
        }
        res = get_paradigms_from_data(item_monocular)
        # print(res)
        self.assertEqual(len(res), 6)

    def test_paradigm_parser_for_ambiguous_parent_paradigm(self):
        item_anesthesia = {
            "Experimental paradigms.Main Paradigm": "Psychedelic Drugs + Anesthesia",
            "Experimental paradigms.Specific Paradigm": "Ketamine (Anesthesia) + Psilocybin (Psychedelic Drugs)",
        }

        res = get_paradigms_from_data(item_anesthesia)
        # print(res)
        self.assertEqual(len(res), 4)

    def test_paradigm_parser_for_only_child_paradigm(self):
        item_resting_state = {
            "Experimental paradigms.Main Paradigm": "Resting State",
            "Experimental paradigms.Specific Paradigm": "",
        }

        res = get_paradigms_from_data(item_resting_state)
        self.assertEqual(len(res), 2)

        item_cueing = {
            "Experimental paradigms.Main Paradigm": "Contextual Cueing + Disorders of Consciousness",
            "Experimental paradigms.Specific Paradigm": "Minimal Consciousness State (Disorders of Consciousness)",
        }

        res = get_paradigms_from_data(item_cueing)
        # print(res)
        self.assertEqual(len(res), 4)

    def test_paradigm_parser_for_multiple_child_paradigms(self):
        item_doc = {
            "Experimental paradigms.Main Paradigm": "Disorders of Consciousness",
            "Experimental paradigms.Specific Paradigm": "Unresponsive Wakefulness Syndrome (Disorders of Consciousness) + Minimal Consciousness State (Disorders of Consciousness)",
        }

        res = get_paradigms_from_data(item_doc)
        # print(res)
        self.assertEqual(len(res), 3)

    def test_paradigm_parser_for_multiple_paradigms_with_subtype(self):
        item_oddball = {
            "Experimental paradigms.Main Paradigm": "Expectation + Sedation",
            "Experimental paradigms.Specific Paradigm": "Oddball(Expectation, Local-Global) + Propofol (Sedation)",
        }
        res = get_paradigms_from_data(item_oddball)

        item_exists = False
        for item in res:
            if (item.name == "Oddball") and (item.sub_type == "Local-Global"):
                item_exists = True
                break
        # print(res)
        self.assertTrue(item_exists)
        self.assertEqual(len(res), 4)

    def test_paradigm_parser_for_multiple_paradigms_with_subtype_and_ambiguous_parent_and_only_child(self):
        item_only_child_and_subtype = {
            "Experimental paradigms.Main Paradigm": "Abnormal Contents of Consciousness + Direct Stimulation + Resting State",
            "Experimental paradigms.Specific Paradigm": "Tinnitus (Abnormal Contents of Consciousness) + Intracranial Stimulation (Direct Stimulation, Auditory Cortex)",
        }

        res = get_paradigms_from_data(item_only_child_and_subtype)
        # print(res)
        self.assertEqual(len(res), 6)
