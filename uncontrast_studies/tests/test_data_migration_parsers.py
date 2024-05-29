from contrast_api.tests.base import BaseTestCase
from uncontrast_studies.parsers.consciousness_measure_parser import resolve_consciousness_measures
from uncontrast_studies.parsers.finding_parser import resolve_uncon_findings
from uncontrast_studies.parsers.sample_parser import resolve_uncon_sample
from uncontrast_studies.parsers.stimulus_parser import (
    resolve_uncon_stimuli_metadata,
    resolve_uncon_prime_stimuli,
    is_target_duplicate,
    resolve_uncon_target_stimuli,
    categorize_prime_stimulus_data,
)
from uncontrast_studies.parsers.suppression_method_parser import resolve_uncon_suppression_method
from uncontrast_studies.parsers.uncon_data_parsers import (
    resolve_uncon_paradigm,
    resolve_uncon_task_type,
    resolve_uncon_processing_domains,
    clean_list_from_data,
)


# Create your tests here.


class UnContrastDataMigrationParsersTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_suppression_method_parser(self):
        item_1 = {
            "Suppression method Main suppression method": "Masking; Parafoveal display",
            "Suppression method Specific suppression method": "Backward pattern masking",
        }
        res = resolve_uncon_suppression_method(item=item_1, index="1")

        self.assertEqual(len(res), 2)
        self.assertEqual(res[1].specific, None)

        item_2 = {
            "Suppression method Main suppression method": "Masking",
            "Suppression method Specific suppression method": "Backward target masking",
        }
        res = resolve_uncon_suppression_method(item=item_2, index="2")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].specific, "Backward target masking")
        self.assertEqual(res[0].main, "Masking")

        item_3 = {
            "Suppression method Main suppression method": "Inattentional blindness",
            "Suppression method Specific suppression method": "",
        }
        res = resolve_uncon_suppression_method(item=item_3, index="3")

        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].specific, None)
        self.assertEqual(res[0].main, "Inattentional blindness")

    def test_paradigm_parser(self):
        item_1 = {"Paradigms Main paradigm": "Priming", "Paradigms Specific paradigm": "Semantic"}
        item_2 = {"Paradigms Main paradigm": "Attention allocation", "Paradigms Specific paradigm": ""}

        res = resolve_uncon_paradigm(item=item_1, index="1")
        self.assertEqual(res.main, "Priming")
        self.assertEqual(res.specific, "Semantic")

        res = resolve_uncon_paradigm(item=item_2, index="2")
        self.assertEqual(res.main, "Attention allocation")
        self.assertEqual(res.specific, "Attention allocation")

    def test_task_parser(self):
        item_1 = {"Tasks Type": "Free viewing"}
        item_2 = {"Tasks Type": "Lexical categorization; Go/No go"}

        res = resolve_uncon_task_type(item=item_1, index="1")
        self.assertEqual(res[0], "Free viewing")
        self.assertEqual(len(res), 1)

        res = resolve_uncon_task_type(item=item_2, index="2")
        self.assertEqual(res[0], "Lexical categorization")
        self.assertEqual(len(res), 2)
        self.assertEqual(res[1], "Go/No go")

    def test_processing_domain_parser(self):
        item_1 = {"Processing domain": "Visual discrimination"}
        item_2 = {"Processing domain": "Numerical;Visual discrimination"}

        res = resolve_uncon_processing_domains(item=item_1, index="1")
        self.assertEqual(res[0], "Visual discrimination")
        self.assertEqual(len(res), 1)

        res = resolve_uncon_processing_domains(item=item_2, index="2")
        self.assertEqual(res[0], "Numerical")
        self.assertEqual(len(res), 2)

    def test_sample_parser(self):
        item_1 = {
            "Samples Type": "Healthy adults",
            "Samples Total": 32,
            "Samples Included": 32,
            "Samples If excluded, how many?": 0,
        }
        item_2 = {
            "Samples Type": "Healthy adults",
            "Samples Total": 43,
            "Samples Included": 42,
            "Samples If excluded, how many?": 1,
        }

        res = resolve_uncon_sample(item=item_1, index="1")
        self.assertEqual(res.sample_type, "healthy_adults")
        self.assertEqual(res.excluded_size, 0)

        res = resolve_uncon_sample(item=item_2, index="2")
        self.assertEqual(res.included_size, 42)
        self.assertEqual(len(res), 4)

    def test_findings_parser(self):
        item_1 = {
            "Experiment's Findings Outcome": "Reaction times; Reaction times; Accuracy; Reaction times; Accuracy",
            "Experiment's Findings Is the effect significant?": "No; missing; Yes; no; yes",
            "Experiment's Findings Number of trials": "1; 2; 3; 4; 5",
            "Experiment's Findings is_important": "missing; missing; missing; missing; missing",
        }
        item_2 = {
            "Experiment's Findings Outcome": "Accuracy (p(C))",
            "Experiment's Findings Is the effect significant?": "Yes",
            "Experiment's Findings Number of trials": "24",
            "Experiment's Findings is_important": "Yes",
        }
        item_3 = {
            "Experiment's Findings Outcome": "Reaction times; Reaction times",
            "Experiment's Findings Is the effect significant?": "missing; missing",
            "Experiment's Findings Number of trials": "46; 46",
            "Experiment's Findings is_important": "No; Yes",
        }

        res = resolve_uncon_findings(item=item_1, index="1")
        # print(res)
        self.assertEqual(len(res), 5)

        res = resolve_uncon_findings(item=item_2, index="2")
        # print(res)
        self.assertEqual(len(res), 1)

        res = resolve_uncon_findings(item=item_3, index="3")
        # print(res)
        self.assertEqual(len(res), 2)

    def test_consciousness_measures_parser(self):
        item_1 = {
            "Consciousness Measures Main type": "Objective",
            "Consciousness Measures Specific type": "Low-level discrimination",
            "Consciousness Measures Phase": "Separate sample",
            "Consciousness Measures Number of trials for the objective measure": "320",
            "Consciousness Measures Is the measure taken from the same participants as the main task?": "No",
            "Consciousness Measures Number of participants of the awareness test": "8",
            "Consciousness Measures Is the performance above chance?": "No",
            "Consciousness Measures Were trials excluded from the analysis based on the measure?": "No",
        }
        item_2 = {
            "Consciousness Measures Main type": "Objective; Subjective",
            "Consciousness Measures Specific type": "High-level discrimination; Perception Awareness Scale (PAS)",
            "Consciousness Measures Phase": "Post-experiment; Trial-by-trial",
            "Consciousness Measures Number of trials for the objective measure": "60",
            "Consciousness Measures Is the measure taken from the same participants as the main task?": "Yes",
            "Consciousness Measures Number of participants of the awareness test": "",
            "Consciousness Measures Is the performance above chance?": "No",
            "Consciousness Measures Were trials excluded from the analysis based on the measure?": "Yes",
        }

        res = resolve_consciousness_measures(item=item_1, index="1")
        # print(res)
        self.assertEqual(len(res), 1)

        res = resolve_consciousness_measures(item=item_2, index="2")
        # print(res)
        self.assertEqual(len(res), 2)

    def test_prime_stimuli_parser(self):
        item_1 = {
            "Stimuli Category": "Numerical",
            "Stimuli Sub-category": "Digits",
            "Stimuli Modality": "Visual",
            "Stimuli Duration": "58",
            "Stimuli Number of different stimuli used in the experiment": "8",
            "Stimuli SOA": "141",
            "Stimuli Mode of presentation": "Liminal",
        }
        item_2 = {
            "Stimuli Category": "Pictures; Lingual",
            "Stimuli Sub-category": "Faces; Words",
            "Stimuli Modality": "Visual",
            "Stimuli Duration": "17; 13",
            "Stimuli Number of different stimuli used in the experiment": "missing",
            "Stimuli SOA": "117; 1",
            "Stimuli Mode of presentation": "Liminal",
        }
        item_6 = {
            "Stimuli Category": "Numerical",
            "Stimuli Sub-category": "Numbers; Digits",
            "Stimuli Modality": "Visual",
            "Stimuli Duration": "33",
            "Stimuli Number of different stimuli used in the experiment": "missing",
            "Stimuli SOA": "33",
            "Stimuli Mode of presentation": "Subliminal",
        }
        item_7 = {
            "Stimuli Category": "Pictures",
            "Stimuli Sub-category": "Objects; Animals",
            "Stimuli Modality": "Visual",
            "Stimuli Duration": "17; 13",
            "Stimuli Number of different stimuli used in the experiment": "missing",
            "Stimuli SOA": "117; 1",
            "Stimuli Mode of presentation": "Liminal",
        }
        item_8 = {
            "Stimuli Category": "Lingual; Numerical",
            "Stimuli Sub-category": "Letters; Numbers",
            "Stimuli Modality": "Visual",
            "Stimuli Duration": "33",
            "Stimuli Number of different stimuli used in the experiment": "missing",
            "Stimuli SOA": "50",
            "Stimuli Mode of presentation": "Subliminal",
        }
        item_9 = {
            "Stimuli Category": "Tactile Stimuli",
            "Stimuli Sub-category": "",
            "Stimuli Modality": "Tactile",
            "Stimuli Duration": "0",
            "Stimuli Number of different stimuli used in the experiment": "missing",
            "Stimuli SOA": "0",
            "Stimuli Mode of presentation": "Liminal",
        }
        item_12 = {
            "Stimuli Category": "Lingual; Numerical",
            "Stimuli Sub-category": "Letters; Words; Digits",
            "Stimuli Modality": "Tactile",
            "Stimuli Duration": "0",
            "Stimuli Number of different stimuli used in the experiment": "missing",
            "Stimuli SOA": "0",
            "Stimuli Mode of presentation": "Liminal",
        }

        res_prime_same_length_singular = resolve_uncon_prime_stimuli(item=item_1, index="1")
        self.assertEqual(len(res_prime_same_length_singular), 1)
        res_prime_same_length_multiple = resolve_uncon_prime_stimuli(item=item_2, index="2")
        self.assertEqual(len(res_prime_same_length_multiple), 2)
        res_prime_multiple_sub_categories_and_singular_numerics = resolve_uncon_prime_stimuli(item=item_6, index="6")
        self.assertEqual(len(res_prime_multiple_sub_categories_and_singular_numerics), 2)
        res_prime_multiple_sub_categories_and_multiple_numerics = resolve_uncon_prime_stimuli(item=item_7, index="7")
        self.assertEqual(len(res_prime_multiple_sub_categories_and_multiple_numerics), 2)
        res_prime_multiple_categories_and_singular_numerics = resolve_uncon_prime_stimuli(item=item_8, index="8")
        self.assertEqual(len(res_prime_multiple_categories_and_singular_numerics), 2)
        res_prime_no_sub_category = resolve_uncon_prime_stimuli(item=item_9, index="9")
        self.assertEqual(len(res_prime_no_sub_category), 1)
        res_prime_multiple_sub_categories_and_multiple_categories = resolve_uncon_prime_stimuli(
            item=item_12, index="12"
        )
        self.assertEqual(len(res_prime_multiple_sub_categories_and_multiple_categories), 3)
        self.assertEqual(res_prime_multiple_sub_categories_and_multiple_categories[0].category, "Lingual")
        self.assertEqual(res_prime_multiple_sub_categories_and_multiple_categories[1].category, "Lingual")
        self.assertEqual(res_prime_multiple_sub_categories_and_multiple_categories[2].category, "Numerical")
        self.assertEqual(res_prime_multiple_sub_categories_and_multiple_categories[0].sub_category, "Letters")
        self.assertEqual(res_prime_multiple_sub_categories_and_multiple_categories[1].sub_category, "Words")
        self.assertEqual(res_prime_multiple_sub_categories_and_multiple_categories[2].sub_category, "Digits")

    def test_target_stimuli_parser(self):
        item_0 = {
            "Stimuli Category 2": "missing",
            "Stimuli Sub-category 2": "missing",
            "Stimuli Modality 2": "missing",
            "Stimuli Number of different stimuli used in the experiment 2": "missing",
        }
        item_3 = {
            "Stimuli Category 2": "Lingual",
            "Stimuli Sub-category 2": "Words",
            "Stimuli Modality 2": "Visual",
            "Stimuli Number of different stimuli used in the experiment 2": "80",
        }
        item_4 = {
            "Stimuli Category 2": "Lingual; Numerical",
            "Stimuli Sub-category 2": "Letters; Digits",
            "Stimuli Modality 2": "Visual",
            "Stimuli Number of different stimuli used in the experiment 2": "8",
        }
        item_5 = {
            "Stimuli Category 2": "Sounds",
            "Stimuli Sub-category 2": "",
            "Stimuli Modality 2": "Visual",
            "Stimuli Number of different stimuli used in the experiment 2": "8",
        }
        item_10 = {
            "Stimuli Category 2": "Pictures",
            "Stimuli Sub-category 2": "Animals; Faces",
            "Stimuli Modality 2": "Visual",
            "Stimuli Number of different stimuli used in the experiment 2": "8",
        }
        item_11 = {
            "Stimuli Category 2": "Lingual; Numerical",
            "Stimuli Sub-category 2": "Letters; Digits",
            "Stimuli Modality 2": "Visual",
            "Stimuli Number of different stimuli used in the experiment 2": "8",
        }

        res_target_missing = resolve_uncon_target_stimuli(item=item_0, index="0")
        self.assertEqual(len(res_target_missing), 0)
        res_target_singular = resolve_uncon_target_stimuli(item=item_3, index="3")
        self.assertEqual(len(res_target_singular), 1)
        res_target_multiple = resolve_uncon_target_stimuli(item=item_4, index="4")
        self.assertEqual(len(res_target_multiple), 2)
        res_target_no_sub_category = resolve_uncon_target_stimuli(item=item_5, index="5")
        self.assertEqual(len(res_target_no_sub_category), 1)
        self.assertEqual(res_target_no_sub_category[0].category, "Sounds")
        self.assertEqual(res_target_no_sub_category[0].sub_category, None)

        res_target_multiple_sub_categories = resolve_uncon_target_stimuli(item=item_10, index="10")
        self.assertEqual(len(res_target_multiple_sub_categories), 2)
        self.assertEqual(res_target_multiple_sub_categories[0].category, "Pictures")
        self.assertEqual(res_target_multiple_sub_categories[0].sub_category, "Animals")
        self.assertEqual(res_target_multiple_sub_categories[1].sub_category, "Faces")

        res_target_multiple_categories_and_sub_categories = resolve_uncon_target_stimuli(item=item_11, index="11")
        self.assertEqual(len(res_target_multiple_categories_and_sub_categories), 2)
        self.assertEqual(res_target_multiple_categories_and_sub_categories[0].category, "Lingual")
        self.assertEqual(res_target_multiple_categories_and_sub_categories[1].category, "Numerical")
        self.assertEqual(res_target_multiple_categories_and_sub_categories[0].sub_category, "Letters")
        self.assertEqual(res_target_multiple_categories_and_sub_categories[1].sub_category, "Digits")

    def test_categorize_prime_stimulus_data(self):
        item_1 = {
            "Stimuli Category": "Numerical",
            "Stimuli Sub-category": "Digits",
            "Stimuli Modality": "Visual",
            "Stimuli Duration": "58",
            "Stimuli Number of different stimuli used in the experiment": "8",
            "Stimuli SOA": "141",
            "Stimuli Mode of presentation": "Liminal",
        }

        res_same_length = categorize_prime_stimulus_data(item=item_1)
        self.assertEqual(res_same_length.is_same_length, True)

        res_target_multiple_categories_and_sub_categories = resolve_uncon_target_stimuli(item=item_11, index="11")
        self.assertEqual(len(res_target_multiple_categories_and_sub_categories), 2)
        self.assertEqual(res_target_multiple_categories_and_sub_categories[0].category, "Lingual")
        self.assertEqual(res_target_multiple_categories_and_sub_categories[1].category, "Numerical")
        self.assertEqual(res_target_multiple_categories_and_sub_categories[0].sub_category, "Letters")
        self.assertEqual(res_target_multiple_categories_and_sub_categories[1].sub_category, "Digits")

    def test_stimulus_metadata_parser(self):
        item = {
            "Stimuli Are there also non-suppressed stimuli that participants had to provide a response to (i.e., a target)?": "Yes",
            "Stimuli Is the non-suppressed stimulus the same as the suppressed stimulus?": "No",
        }

        res = resolve_uncon_stimuli_metadata(item=item, index="1")
        self.assertEqual(res.is_target_stimuli, True)
        self.assertEqual(res.is_target_same_as_prime, False)

    def test_is_target_duplicate_helper(self):
        item_identical = {
            "Stimuli Category": "Lingual",
            "Stimuli Sub-category": "Words",
            "Stimuli Modality": "Visual",
            "Stimuli Number of different stimuli used in the experiment": "80",
            "Stimuli Category 2": "Lingual",
            "Stimuli Sub-category 2": "Words",
            "Stimuli Modality 2": "Visual",
            "Stimuli Number of different stimuli used in the experiment 2": "80",
        }

        item_different_sub_category = {
            "Stimuli Category": "Lingual",
            "Stimuli Sub-category": "Words",
            "Stimuli Modality": "Visual",
            "Stimuli Number of different stimuli used in the experiment": "80",
            "Stimuli Category 2": "Lingual",
            "Stimuli Sub-category 2": "Letters",
            "Stimuli Modality 2": "Visual",
            "Stimuli Number of different stimuli used in the experiment 2": "80",
        }

        item_different_num_of_stimuli = {
            "Stimuli Category": "Lingual",
            "Stimuli Sub-category": "Words",
            "Stimuli Modality": "Visual",
            "Stimuli Number of different stimuli used in the experiment": "missing",
            "Stimuli Category 2": "Lingual",
            "Stimuli Sub-category 2": "Words",
            "Stimuli Modality 2": "Visual",
            "Stimuli Number of different stimuli used in the experiment 2": "80",
        }

        item_different_modality = {
            "Stimuli Category": "Lingual",
            "Stimuli Sub-category": "Words",
            "Stimuli Modality": "Visual",
            "Stimuli Number of different stimuli used in the experiment": "80",
            "Stimuli Category 2": "Lingual",
            "Stimuli Sub-category 2": "Words",
            "Stimuli Modality 2": "Auditory",
            "Stimuli Number of different stimuli used in the experiment 2": "80",
        }

        res = is_target_duplicate(item_identical)
        self.assertTrue(res)
        res = is_target_duplicate(item_different_sub_category)
        self.assertFalse(res)
        res = is_target_duplicate(item_different_num_of_stimuli)
        self.assertFalse(res)
        res = is_target_duplicate(item_different_modality)
        self.assertFalse(res)

    def test_clean_list_from_data(self):
        data_item_text = "Words; Digits"
        data_item_integers = "126; 126; 252"
        data_item_floats = "23; 94; 58.5"

        res_text = clean_list_from_data(data_item_text)
        self.assertEqual(res_text, ["Words", "Digits"])
        res_integers = clean_list_from_data(data_item_integers, integer=True)
        self.assertEqual(res_integers, [126, 126, 252])
        res_floats = clean_list_from_data(data_item_floats, integer=True)
        self.assertEqual(res_floats, [23, 94, 58.5])
