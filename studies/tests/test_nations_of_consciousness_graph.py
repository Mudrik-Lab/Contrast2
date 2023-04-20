from django.urls import reverse
from rest_framework import status

from studies.choices import InterpretationsChoices
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
        israeli_study = self.given_study_exists(title="Israeli study", countries=["IL"],
                                                DOI="10.1016/j.cortex.2017.07.011", year=2002)
        british_israeli_study = self.given_study_exists(title="british", countries=["UK", "IL"],
                                                        DOI="10.1016/j.cortex.2017.07.012", year=2004)

        gnw_parent_theory = self.given_theory_exists(parent=None, name="GNW")
        rpt_parent_theory = self.given_theory_exists(parent=None, name="RPT")
        gnw_child_theory = self.given_theory_exists(parent=gnw_parent_theory, name="GNW_child")
        rpt_child_theory = self.given_theory_exists(parent=rpt_parent_theory, name="RPT_child")

        israeli_study_experiment = self.given_experiment_exists_for_study(study=israeli_study)
        israeli_study_experiment_2 = self.given_experiment_exists_for_study(study=israeli_study)
        british_israeli_study_experiment = self.given_experiment_exists_for_study(study=british_israeli_study)

        self.given_interpretation_exist(experiment=israeli_study_experiment,
                                        theory=gnw_child_theory, interpretation_type=InterpretationsChoices.PRO)
        self.given_interpretation_exist(experiment=israeli_study_experiment_2,
                                        theory=gnw_child_theory, interpretation_type=InterpretationsChoices.PRO)
        self.given_interpretation_exist(experiment=british_israeli_study_experiment,
                                        theory=rpt_child_theory, interpretation_type=InterpretationsChoices.PRO)
        self.given_interpretation_exist(experiment=british_israeli_study_experiment,
                                        theory=gnw_child_theory, interpretation_type=InterpretationsChoices.CHALLENGES)

        target_url = self.reverse_with_query_params("experiments-graphs-nations-of-consciousness", theory=[gnw_parent_theory.name,
                                                                                                           rpt_parent_theory.name ])
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
        self.assertEqual(first_result["country"], "IL")
        self.assertEqual(first_result["count"], 1)
        self.assertEqual(first_result["theory"], "GNW")
        self.assertEqual(second_result["country"], "IL")
        self.assertEqual(second_result["count"], 1)
        self.assertEqual(second_result["theory"], "RPT")
        self.assertEqual(third_result["country"], "UK")
        self.assertEqual(third_result["count"], 1)
        self.assertEqual(third_result["theory"], "RPT")
