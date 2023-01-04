from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from studies.choices import TypeOfConsciousnessChoices, ReportingChoices, TheoryDrivenChoices, InterpretationsChoices
from studies.models import Experiment, Theory, Interpretation
from studies.tests.base import BaseTestCase


# Create your tests here.
class ExperimentsViewSetTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_experiments_endpoint_is_responding_to_list(self):
        target_url = reverse("experiments-list")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_nations_of_consciousness_data(self):
        """
        provide graph_type=nations_of_consciousness, min_experiments?=int
        returns experiments grouped by country and interpretations (positive to theory)
        """
        israeli_study = self.given_study_exists(title="Israeli study", countries=["IL"],
                                                DOI="10.1016/j.cortex.2017.07.011")
        british_israeli_study = self.given_study_exists(title="british", countries=["UK", "IL"],
                                                        DOI="10.1016/j.cortex.2017.07.012")

        gnw_parent_theory = self.given_theory_exists(parent=None, name="GNW")
        rpt_parent_theory = self.given_theory_exists(parent=None, name="RPT")
        gnw_child_theory = self.given_theory_exists(parent=gnw_parent_theory, name="GNW_child")
        rpt_child_theory = self.given_theory_exists(parent=rpt_parent_theory, name="RPT_child")

        israeli_study_experiment = self.given_experiment_exists_for_study(study=israeli_study)
        israeli_study_experiment_2 = self.given_experiment_exists_for_study(study=israeli_study)
        british_israeli_study_experiment = self.given_experiment_exists_for_study(study=british_israeli_study)

        self.given_interpretation_exist(experiment=israeli_study_experiment,
                                        theory=gnw_child_theory, type=InterpretationsChoices.PRO)
        self.given_interpretation_exist(experiment=israeli_study_experiment_2,
                                        theory=gnw_child_theory, type=InterpretationsChoices.PRO)
        self.given_interpretation_exist(experiment=british_israeli_study_experiment,
                                        theory=rpt_child_theory, type=InterpretationsChoices.PRO)
        self.given_interpretation_exist(experiment=british_israeli_study_experiment,
                                        theory=gnw_child_theory, type=InterpretationsChoices.CHALLENGES)

        target_url = self.reverse_with_query_params("experiments-list", graph_type="nations_of_consciousness")
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

    def test_publications_by_theory_family_data(self):
        """
        provide graph_type=publications_by_theory, min_experiments?=int, theory=GNW
        group by publications names
        """
        pass

    def test_frequencies_graph(self):
        pass

    def test_timings_graphs(self):
        pass

    def test_theory_driven_by_interpretations(self):
        """
        is_reporting[]=true, TypeOfConsciousness[]=state
        hint: use request.query_params.getlist
        """
        pass

    def given_experiment_exists_for_study(self, study, **kwargs) -> Experiment:
        default_experiment = dict(study=study,
                                  finding_description="look what we found",
                                  is_reporting=ReportingChoices.NO_REPORT,
                                  theory_driven=TheoryDrivenChoices.POST_HOC,
                                  type_of_consciousness=TypeOfConsciousnessChoices.CONTENT)

        experiment_params = {**default_experiment, **kwargs}
        experiment, created = Experiment.objects.get_or_create(**experiment_params)
        return experiment

    def reverse_with_query_params(self, url_name: str, *args, **queryparams) -> str:
        params = "&".join([f"{k}={v}" for k, v in queryparams.items()])
        url = reverse(url_name, args=args)
        url = f'{url}?{params}'
        return url

    def given_theory_exists(self, name:str, parent:Theory = None):
        theory, created = Theory.objects.get_or_create(parent=parent, name=name)
        return theory

    def given_interpretation_exist(self, experiment:Experiment, theory:Theory, type: str):
        interpretation, created = Interpretation.objects.get_or_create(experiment=experiment, theory=theory, type=type)
        return interpretation
