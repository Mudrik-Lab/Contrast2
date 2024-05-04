
from contrast_api.tests.base import BaseTestCase
from uncontrast_studies.parsers.suppression_method_parser import resolve_uncon_suppression_method
from uncontrast_studies.parsers.uncon_data_parsers import resolve_uncon_paradigm, resolve_uncon_task


# Create your tests here.


class UnContrastDataMigrationParsersTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_suppression_method_parser(self):
        item = {"Suppression method Main suppression method": "Masking; Parafoveal display",
                "Suppression method Specific suppression method": "Backward pattern masking"}

        res = resolve_uncon_suppression_method(item=item, index="1")

        self.assertEqual(len(res), 2)
        self.assertEqual(res[1].specific, None)

    def test_paradigm_parser(self):
        item = {"Paradigms Main paradigm": "Priming",
                "Paradigms Specific paradigm": "Semantic"}

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
