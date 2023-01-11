from typing import Optional

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from studies.choices import TypeOfConsciousnessChoices, ReportingChoices, TheoryDrivenChoices, InterpretationsChoices, \
    ExperimentTypeChoices
from studies.models import Experiment, Theory, Interpretation, Paradigm, Measure, MeasureType, TaskType, Task
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

        """
        pass

    def test_across_the_years(self):
        """
        provide graph_type=across_the_years, min_experiments?=int, breakdown=str
        returns experiments grouped by breakdown and by year within breakdown
        """
        israeli_study = self.given_study_exists(title="Israeli study", countries=["IL"],
                                                DOI="10.1016/j.cortex.2017.07.011", year=2002)
        british_israeli_study = self.given_study_exists(title="british", countries=["UK", "IL"],
                                                        DOI="10.1016/j.cortex.2017.07.012", year=2004)

        gnw_parent_theory = self.given_theory_exists(parent=None, name="GNW")
        rpt_parent_theory = self.given_theory_exists(parent=None, name="RPT")
        gnw_child_theory = self.given_theory_exists(parent=gnw_parent_theory, name="GNW_child")
        rpt_child_theory = self.given_theory_exists(parent=rpt_parent_theory, name="RPT_child")

        masking_parent_paradigm = self.given_paradigm_exists(name="masking_parent_paradigm")
        masking_child_paradigm = self.given_paradigm_exists(name="masking_child_paradigm",
                                                            parent=masking_parent_paradigm)
        different_parent_paradigm = self.given_paradigm_exists(name="different_parent_paradigm")
        different_child_paradigm = self.given_paradigm_exists(name="different_child_paradigm",
                                                              parent=different_parent_paradigm)
        another_different_child_paradigm = self.given_paradigm_exists(name="zz_another_different_child_paradigm",
                                                                      parent=different_parent_paradigm)

        israeli_study_experiment = self.given_experiment_exists_for_study(study=israeli_study,
                                                                          paradigms=[masking_child_paradigm])
        israeli_study_experiment_2 = self.given_experiment_exists_for_study(study=israeli_study,
                                                                            finding_description="brave new world",
                                                                            paradigms=[different_child_paradigm,
                                                                                       masking_child_paradigm])
        british_israeli_study_experiment = self.given_experiment_exists_for_study(study=british_israeli_study,
                                                                                  paradigms=[
                                                                                      another_different_child_paradigm])

        first_measure = self.given_measure_exists(experiment_id=israeli_study_experiment.id, measure_type="a_first_measure")
        second_measure = self.given_measure_exists(experiment_id=israeli_study_experiment.id, measure_type="b_second_measure")
        third_measure_with_second_type = self.given_measure_exists(experiment_id=israeli_study_experiment_2.id, measure_type="b_second_measure")
        fourth_measure = self.given_measure_exists(experiment_id=british_israeli_study_experiment.id, measure_type="c_third_measure")

        self._test_across_the_years_breakdown_paradigm_family(different_parent_paradigm, masking_parent_paradigm)
        self._test_across_the_years_breakdown_paradigm(different_child_paradigm, another_different_child_paradigm,
                                                       masking_child_paradigm)
        self._test_across_the_years_breakdown_measures(first_measure, second_measure,
                                                       third_measure_with_second_type, fourth_measure)

    def _test_across_the_years_breakdown_paradigm_family(self, different_parent_paradigm, masking_parent_paradigm):
        target_url = self.reverse_with_query_params("experiments-list", graph_type="across_the_years",
                                                    breakdown="paradigm_family")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        first_series = res.data[0]
        second_series = res.data[1]
        self.assertEqual(first_series["series_name"], different_parent_paradigm.name)
        self.assertEqual(second_series["series_name"], masking_parent_paradigm.name)
        # masking_child_paradigm exists only on the isreali study from 2002 on two different experiments
        self.assertDictEqual(second_series["series"][0], dict(year=2002, value=2))
        # While different_child_paradigm is on both studies, so one in 2002 and one in 2004
        self.assertDictEqual(first_series["series"][0], dict(year=2002, value=1))
        self.assertDictEqual(first_series["series"][1], dict(year=2004, value=1))

    def _test_across_the_years_breakdown_paradigm(self, different_child_paradigm, another_different_child_paradigm,
                                                  masking_child_paradigm):
        target_url = self.reverse_with_query_params("experiments-list", graph_type="across_the_years",
                                                    breakdown="paradigm")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)
        first_series = res.data[0]
        second_series = res.data[1]
        third_series = res.data[2]
        self.assertEqual(first_series["series_name"], different_child_paradigm.name)
        self.assertEqual(second_series["series_name"], masking_child_paradigm.name)
        self.assertEqual(third_series["series_name"], another_different_child_paradigm.name)
        # masking_child_paradigm exists only on the isreali study from 2002 on two different experiments
        self.assertDictEqual(second_series["series"][0], dict(year=2002, value=2))
        self.assertDictEqual(first_series["series"][0], dict(year=2002, value=1))
        self.assertDictEqual(third_series["series"][0], dict(year=2004, value=1))

    def _test_across_the_years_breakdown_measures(self, first_measure, second_measure,
                                                  third_measure, fourth_measure):
        target_url = self.reverse_with_query_params("experiments-list", graph_type="across_the_years",
                                                    breakdown="measure")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 3)
        first_series = res.data[0]
        second_series = res.data[1]
        third_series = res.data[2]

        self.assertEqual(first_series["series_name"], first_measure.type.name)
        self.assertEqual(second_series["series_name"], second_measure.type.name)
        self.assertEqual(third_series["series_name"], fourth_measure.type.name)
        # second measure type happened twice
        self.assertDictEqual(first_series["series"][0], dict(year=2002, value=1))
        self.assertDictEqual(second_series["series"][0], dict(year=2002, value=2))
        self.assertDictEqual(third_series["series"][0], dict(year=2004, value=1))

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
                                  type=ExperimentTypeChoices.NEUROSCIENTIFIC,
                                  type_of_consciousness=TypeOfConsciousnessChoices.CONTENT)
        paradigms = kwargs.pop("paradigms")

        experiment_params = {**default_experiment, **kwargs}
        experiment, created = Experiment.objects.get_or_create(**experiment_params)
        if paradigms:
            for item in paradigms:
                experiment.paradigms.add(item)
        return experiment

    def reverse_with_query_params(self, url_name: str, *args, **queryparams) -> str:
        params = "&".join([f"{k}={v}" for k, v in queryparams.items()])
        url = reverse(url_name, args=args)
        url = f'{url}?{params}'
        return url

    def given_theory_exists(self, name: str, parent: Theory = None):
        theory, created = Theory.objects.get_or_create(parent=parent, name=name)
        return theory

    def given_interpretation_exist(self, experiment: Experiment, theory: Theory, type: str):
        interpretation, created = Interpretation.objects.get_or_create(experiment=experiment, theory=theory, type=type)
        return interpretation

    def given_paradigm_exists(self, name: str, parent: Optional[Paradigm] = None):
        params = dict(name=name, parent=parent)
        paradigm, created = Paradigm.objects.get_or_create(**params)
        return paradigm

    def given_measure_exists(self, experiment_id, measure_type, notes: Optional[str] = None):
        measure_type_instance, created = MeasureType.objects.get_or_create(name=measure_type)
        params = dict(experiment_id=experiment_id, type=measure_type_instance, notes=notes)

        measure, created = Measure.objects.get_or_create(**params)
        return measure

    def given_task_exists(self, experiment_id, task_type, description: Optional[str] = None):
        task_type_instance, created = TaskType.objects.get_or_create(name=task_type)
        params = dict(experiment_id=experiment_id, type=task_type_instance, description=description)

        task, created = Task.objects.get_or_create(**params)
        return task
