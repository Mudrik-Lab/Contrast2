from rest_framework import status

from contrast_api.choices import InterpretationsChoices
from contrast_api.tests.base import BaseTestCase


# Create your tests here.
class NationsOfConsciousnessViewSetTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_nations_of_consciousness_data(self):
        """
        provide graph_type=nations_of_consciousness, min_experiments?=int
        returns experiments grouped by country and interpretations (positive to theory)
        """
        israeli_study = self.given_study_exists(
            title="Israeli study", countries=["IL"], DOI="10.1016/j.cortex.2017.07.011", year=2002
        )
        british_israeli_study = self.given_study_exists(
            title="british", countries=["GB", "IL"], DOI="10.1016/j.cortex.2017.07.012", year=2004
        )

        self.gnw_parent_theory = self.given_theory_exists(parent=None, name="GNW", acronym="GNW")
        self.rpt_parent_theory = self.given_theory_exists(parent=None, name="RPT", acronym="RPT")
        self.gnw_child_theory = self.given_theory_exists(parent=self.gnw_parent_theory, name="GNW_child")
        self.rpt_child_theory = self.given_theory_exists(parent=self.rpt_parent_theory, name="RPT_child")

        israeli_study_experiment = self.given_experiment_exists_for_study(study=israeli_study)
        israeli_study_experiment_2 = self.given_experiment_exists_for_study(study=israeli_study)
        british_israeli_study_experiment = self.given_experiment_exists_for_study(study=british_israeli_study)

        self.given_interpretation_exist(
            experiment=israeli_study_experiment,
            theory=self.gnw_child_theory,
            interpretation_type=InterpretationsChoices.PRO,
        )
        self.given_interpretation_exist(
            experiment=israeli_study_experiment_2,
            theory=self.gnw_child_theory,
            interpretation_type=InterpretationsChoices.PRO,
        )
        self.given_interpretation_exist(
            experiment=british_israeli_study_experiment,
            theory=self.rpt_child_theory,
            interpretation_type=InterpretationsChoices.PRO,
        )
        self.given_interpretation_exist(
            experiment=british_israeli_study_experiment,
            theory=self.gnw_child_theory,
            interpretation_type=InterpretationsChoices.CHALLENGES,
        )

        target_url = self.reverse_with_query_params(
            "experiments-graphs-nations-of-consciousness",
            theory=[self.gnw_parent_theory.name, self.rpt_parent_theory.name],
        )
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        """
        First we'll check for 3 results. why three? 
        IL GNW 2
        IL RPT 1
        UK RPT 1
        there is no 2 more GNW on IL and UK because it's a challenging interpretations
        """
        self.assertEqual(len(res.data), 3)
        first_result = res.data[0]
        second_result = res.data[1]
        third_result = res.data[2]
        # verify alphebetical order by counry and theory name
        self.assertEqual(second_result["country"], "ISR")
        self.assertEqual(second_result["theory"], "GNW")
        self.assertEqual(second_result["total"], 2)  # total for Israel
        self.assertEqual(second_result["value"], 1)
        self.assertEqual(third_result["country"], "ISR")
        self.assertEqual(third_result["value"], 1)
        self.assertEqual(third_result["theory"], "RPT")

        self.assertEqual(first_result["country"], "GBR")
        self.assertEqual(first_result["value"], 1)
        self.assertEqual(first_result["theory"], "RPT")
