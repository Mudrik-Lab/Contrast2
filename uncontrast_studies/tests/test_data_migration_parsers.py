
from contrast_api.tests.base import BaseTestCase
from uncontrast_studies.parsers.uncon_data_parsers import resolve_uncon_suppression_method


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

