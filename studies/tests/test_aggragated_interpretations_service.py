from contrast_api.tests.base import BaseTestCase
from studies.choices import InterpretationsChoices, AggregatedInterpretationsChoices
from studies.services.aggregated_Interpretations_svc import AggregatedInterpretationService, AggregatedInterpretationDTO


class AggregatedInterpretationsServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_resolve_simple_pro(self):
        current = [AggregatedInterpretationDTO("GNW", "GNW", InterpretationsChoices.PRO)]
        svc = AggregatedInterpretationService(current)
        result = svc.resolve()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].parent_theory_names, "GNW")

    def test_resolve_simple_pro_and_challenges(self):
        current = [
            AggregatedInterpretationDTO("GNW", "GNT", InterpretationsChoices.PRO),
            AggregatedInterpretationDTO("ITT", "ITT", InterpretationsChoices.CHALLENGES),
        ]
        svc = AggregatedInterpretationService(current)
        result = svc.resolve()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].parent_theory_names, "GNW")
        self.assertEqual(result[0].type, AggregatedInterpretationsChoices.PRO)
        self.assertEqual(result[1].parent_theory_names, "ITT")
        self.assertEqual(result[1].type, AggregatedInterpretationsChoices.CHALLENGES)

    def test_all_neutral_returns_empty_list(self):
        current = [
            AggregatedInterpretationDTO("GNW", "GNW", InterpretationsChoices.NEUTRAL),
            AggregatedInterpretationDTO("ITT", "ITT", InterpretationsChoices.NEUTRAL),
        ]
        svc = AggregatedInterpretationService(current)
        result = svc.resolve()
        self.assertEqual(len(result), 0)

    def test_multiple_pro_and_multiple_challenges(self):
        current = [  # Note we provide in non Alphabetical ordr to test
            AggregatedInterpretationDTO("RPT", "RPT", InterpretationsChoices.PRO),
            AggregatedInterpretationDTO("GNW", "GNW", InterpretationsChoices.PRO),
            AggregatedInterpretationDTO("IIT", "ITT", InterpretationsChoices.CHALLENGES),
            AggregatedInterpretationDTO("HOT", "HOT", InterpretationsChoices.CHALLENGES),
        ]
        svc = AggregatedInterpretationService(current)
        result = svc.resolve()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].parent_theory_names, "GNW & RPT")  # Alphabetical order
        self.assertEqual(result[0].type, AggregatedInterpretationsChoices.PRO)  # Alphabetical order
        self.assertEqual(result[1].parent_theory_names, "HOT & IIT")
        self.assertEqual(result[1].type, AggregatedInterpretationsChoices.CHALLENGES)
