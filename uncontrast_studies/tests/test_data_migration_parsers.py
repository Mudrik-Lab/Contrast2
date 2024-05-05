from contrast_api.tests.base import BaseTestCase
from uncontrast_studies.parsers.finding_parser import resolve_uncon_findings
from uncontrast_studies.parsers.sample_parser import resolve_uncon_sample
from uncontrast_studies.parsers.suppression_method_parser import resolve_uncon_suppression_method
from uncontrast_studies.parsers.uncon_data_parsers import (
    resolve_uncon_paradigm,
    resolve_uncon_task,
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

        res = resolve_uncon_task(item=item_1, index="1")
        self.assertEqual(res[0], "Free viewing")
        self.assertEqual(len(res), 1)

        res = resolve_uncon_task(item=item_2, index="2")
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
        print(res)
        self.assertEqual(len(res), 5)

        res = resolve_uncon_findings(item=item_2, index="2")
        print(res)
        self.assertEqual(len(res), 1)

        res = resolve_uncon_findings(item=item_3, index="3")
        print(res)
        self.assertEqual(len(res), 2)

    def test_consciousness_measures_parser(self):
        pass

    def test_stimuli_parser(self):
        pass
