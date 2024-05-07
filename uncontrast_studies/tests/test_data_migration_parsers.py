from contrast_api.tests.base import BaseTestCase
from uncontrast_studies.parsers.consciousness_measure_parser import resolve_consciousness_measures
from uncontrast_studies.parsers.finding_parser import resolve_uncon_findings
from uncontrast_studies.parsers.sample_parser import resolve_uncon_sample
from uncontrast_studies.parsers.stimulus_parser import resolve_uncon_stimuli_metadata, resolve_uncon_stimuli, \
    is_target_duplicate
from uncontrast_studies.parsers.suppression_method_parser import resolve_uncon_suppression_method
from uncontrast_studies.parsers.uncon_data_parsers import (
    resolve_uncon_paradigm,
    resolve_uncon_task_type,
    resolve_uncon_processing_domains,
)


# Create your tests here.


class UnContrastDataMigrationParsersTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_suppression_method_parser(self):
        item = {
            "Suppression method Main suppression method": "Masking; Parafoveal display",
            "Suppression method Specific suppression method": "Backward pattern masking",
        }

        res = resolve_uncon_suppression_method(item=item, index="1")

        self.assertEqual(len(res), 2)
        self.assertEqual(res[1].specific, None)

    def test_paradigm_parser(self):
        item = {"Paradigms Main paradigm": "Priming", "Paradigms Specific paradigm": "Semantic"}

        res = resolve_uncon_paradigm(item=item, index="1")

        self.assertEqual(res.main, "Priming")
        self.assertEqual(res.specific, "Semantic")

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
        self.assertEqual(res.excluded_size, None)

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
            "Experiment's Findings Outcome": "Accuracy (notes for finding)",
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

    def test_stimuli_parser(self):
        item_1 = {
            "Stimuli Category": "Lingual",
            "Stimuli Sub-category": "Words",
            "Stimuli Modality": "Visual",
            "Stimuli Duration": "33",
            "Stimuli Number of different stimuli used in the experiment": "missing",
            "Stimuli SOA": "33",
            "Stimuli Mode of presentation": "Subliminal",
        }
        item_2 = {
            "Stimuli Category": "Pictures; Lingual",
            "Stimuli Sub-category": "Faces; Words",
            "Stimuli Modality": "Visual",
            "Stimuli Duration": "17",
            "Stimuli Number of different stimuli used in the experiment": "missing",
            "Stimuli SOA": "117",
            "Stimuli Mode of presentation": "Liminal",
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

        res_prime_singular = resolve_uncon_stimuli(item=item_1, index="1", prime=True)
        self.assertEqual(len(res_prime_singular), 1)
        res_prime_multiple = resolve_uncon_stimuli(item=item_2, index="2", prime=True)
        self.assertEqual(len(res_prime_multiple), 2)

        res_target_singular = resolve_uncon_stimuli(item=item_3, index="3", prime=False)
        self.assertEqual(len(res_target_singular), 1)
        res_target_multiple = resolve_uncon_stimuli(item=item_4, index="4", prime=False)
        self.assertEqual(len(res_target_multiple), 2)

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
            "Stimuli Number of different stimuli used in the experiment 2": "80"
        }

        item_different_sub_category = {
            "Stimuli Category": "Lingual",
            "Stimuli Sub-category": "Words",
            "Stimuli Modality": "Visual",
            "Stimuli Number of different stimuli used in the experiment": "80",
            "Stimuli Category 2": "Lingual",
            "Stimuli Sub-category 2": "Letters",
            "Stimuli Modality 2": "Visual",
            "Stimuli Number of different stimuli used in the experiment 2": "80"
        }

        item_different_num_of_stimuli = {
            "Stimuli Category": "Lingual",
            "Stimuli Sub-category": "Words",
            "Stimuli Modality": "Visual",
            "Stimuli Number of different stimuli used in the experiment": "missing",
            "Stimuli Category 2": "Lingual",
            "Stimuli Sub-category 2": "Words",
            "Stimuli Modality 2": "Visual",
            "Stimuli Number of different stimuli used in the experiment 2": "80"
        }

        item_different_modality = {
            "Stimuli Category": "Lingual",
            "Stimuli Sub-category": "Words",
            "Stimuli Modality": "Visual",
            "Stimuli Number of different stimuli used in the experiment": "80",
            "Stimuli Category 2": "Lingual",
            "Stimuli Sub-category 2": "Words",
            "Stimuli Modality 2": "Auditory",
            "Stimuli Number of different stimuli used in the experiment 2": "80"
        }

        res = is_target_duplicate(item_identical)
        self.assertTrue(res)
        res = is_target_duplicate(item_different_sub_category)
        self.assertFalse(res)
        res = is_target_duplicate(item_different_num_of_stimuli)
        self.assertFalse(res)
        res = is_target_duplicate(item_different_modality)
        self.assertFalse(res)

