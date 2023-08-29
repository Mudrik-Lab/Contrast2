from rest_framework import status

from studies.choices import ReportingChoices, InterpretationsChoices
from contrast_api.tests.base import BaseTestCase


# Create your tests here.
class ParameterDistributionBarGraphTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def _given_world_setup(self):
        israeli_study = self.given_study_exists(title="Israeli study", countries=["IL"],
                                                DOI="10.1016/j.cortex.2017.07.011", year=2002)
        british_israeli_study = self.given_study_exists(title="british", countries=["UK", "IL"],
                                                        DOI="10.1016/j.cortex.2017.07.012", year=2004)
        self.gnw_parent_theory = self.given_theory_exists(parent=None, name="GNW", acronym="GNW")
        self.rpt_parent_theory = self.given_theory_exists(parent=None, name="RPT", acronym="RPT")
        gnw_child_theory = self.given_theory_exists(parent=self.gnw_parent_theory, name="GNW_child")
        rpt_child_theory = self.given_theory_exists(parent=self.rpt_parent_theory, name="RPT_child")
        masking_parent_paradigm = self.given_paradigm_exists(name="masking_parent_paradigm")
        masking_child_paradigm = self.given_paradigm_exists(name="masking_child_paradigm",
                                                            parent=masking_parent_paradigm)
        different_parent_paradigm = self.given_paradigm_exists(name="different_parent_paradigm")
        different_child_paradigm = self.given_paradigm_exists(name="different_child_paradigm",
                                                              parent=different_parent_paradigm)
        another_different_child_paradigm = self.given_paradigm_exists(name="zz_another_different_child_paradigm",
                                                                      parent=different_parent_paradigm)
        first_technique = self.given_technique_exists("a_first_technique")
        second_technique = self.given_technique_exists("b_second_technique")
        israeli_study_experiment = self.given_experiment_exists_for_study(study=israeli_study,
                                                                          paradigms=[masking_child_paradigm],
                                                                          is_reporting=ReportingChoices.NO_REPORT,
                                                                          techniques=[second_technique])
        israeli_study_experiment_2 = self.given_experiment_exists_for_study(study=israeli_study,
                                                                            results_summary="brave new world",
                                                                            techniques=[second_technique],
                                                                            is_reporting=ReportingChoices.NO_REPORT,
                                                                            paradigms=[different_child_paradigm,
                                                                                       masking_child_paradigm])
        british_israeli_study_experiment = self.given_experiment_exists_for_study(study=british_israeli_study,
                                                                                  techniques=[first_technique,
                                                                                              second_technique],
                                                                                  is_reporting=ReportingChoices.BOTH,
                                                                                  paradigms=[
                                                                                      masking_child_paradigm,
                                                                                      another_different_child_paradigm])
        # setup:
        """
        masking parent paradigm 
         gnw -pro: 2 against: 1
         rpt pro:  1 against: 1
        different parent paradigm - 
         gnw - pro: 1 against: 1
         rpt - pro:1  against: 
        """
        self.given_interpretation_exist(experiment=israeli_study_experiment,  # masking_child_paradigm
                                        theory=gnw_child_theory, interpretation_type=InterpretationsChoices.PRO)

        self.given_interpretation_exist(experiment=british_israeli_study_experiment,
                                        # masking_child_paradigm, different
                                        theory=gnw_child_theory, interpretation_type=InterpretationsChoices.CHALLENGES)

        self.given_interpretation_exist(experiment=israeli_study_experiment,  # masking_child_paradigm
                                        theory=rpt_child_theory, interpretation_type=InterpretationsChoices.CHALLENGES)

        self.given_interpretation_exist(experiment=israeli_study_experiment_2,  # masking_child_paradigm, different
                                        theory=gnw_child_theory, interpretation_type=InterpretationsChoices.PRO)

        self.given_interpretation_exist(experiment=british_israeli_study_experiment,
                                        # masking_child_paradigm, different
                                        theory=rpt_child_theory, interpretation_type=InterpretationsChoices.PRO)
        first_measure = self.given_measure_exists(experiment_id=israeli_study_experiment.id,
                                                  measure_type="a_first_measure")
        second_measure = self.given_measure_exists(experiment_id=israeli_study_experiment.id,
                                                   measure_type="b_second_measure")
        third_measure_with_second_type = self.given_measure_exists(experiment_id=israeli_study_experiment_2.id,
                                                                   measure_type="b_second_measure")
        fourth_measure = self.given_measure_exists(experiment_id=british_israeli_study_experiment.id,
                                                   measure_type="c_third_measure")
        return another_different_child_paradigm, different_child_paradigm, different_parent_paradigm, first_measure, first_technique, fourth_measure, masking_child_paradigm, masking_parent_paradigm, second_measure, second_technique, third_measure_with_second_type

    def test_parameters_distribution_bar_breakdown_paradigm_family(self):
        another_different_child_paradigm, \
        different_child_paradigm, \
        different_parent_paradigm, \
        first_measure, first_technique, \
        fourth_measure, masking_child_paradigm, \
        masking_parent_paradigm, second_measure, \
        second_technique, third_measure_with_second_type = self._given_world_setup()
        target_url = self.reverse_with_query_params("experiments-graphs-parameters-distribution-bar",
                                                    breakdown="paradigm_family", theory=self.gnw_parent_theory.id)
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 2)  # as gnw child interperation to two paradigms
        """
        masking parent paradigm 
         gnw -pro: 2 against: 1
         rpt pro:  1 against: 1
        different parent paradigm - 
         gnw - pro: 1 against: 1
         rpt - pro:1  against: """
        first_series = res.data[0]
        second_series = res.data[1]
        self.assertEqual(first_series["series_name"], masking_parent_paradigm.name)  # 3 total
        self.assertEqual(second_series["series_name"], different_parent_paradigm.name)  # 2

        self.assertEqual(first_series["series"][0]["key"], InterpretationsChoices.PRO)
        self.assertEqual(first_series["series"][0]["value"], 2)

        self.assertEqual(first_series["series"][1]["key"], InterpretationsChoices.CHALLENGES)
        self.assertEqual(first_series["series"][1]["value"], 1)

        self.assertEqual(second_series["series"][0]["key"], InterpretationsChoices.PRO)
        self.assertEqual(second_series["series"][0]["value"], 1)

        self.assertEqual(second_series["series"][1]["key"], InterpretationsChoices.CHALLENGES)
        self.assertEqual(second_series["series"][1]["value"], 1)

        target_url = self.reverse_with_query_params("experiments-graphs-parameters-distribution-bar",
                                                    breakdown="paradigm_family", theory=self.rpt_parent_theory.id)
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        first_series = res.data[0]
        second_series = res.data[1]
        self.assertEqual(first_series["series_name"], masking_parent_paradigm.name)  # 2 total
        self.assertEqual(second_series["series_name"], different_parent_paradigm.name)  # 1

    def test_all_options_sanity_test(self):
        """
        This is just a basic sanity test, that nothing throws an exception, later we might add more here
        """
        another_different_child_paradigm, \
        different_child_paradigm, \
        different_parent_paradigm, \
        first_measure, first_technique, \
        fourth_measure, masking_child_paradigm, \
        masking_parent_paradigm, second_measure, \
        second_technique, third_measure_with_second_type = self._given_world_setup()
        for breakdown in {
            "paradigm_family",
            "paradigm",
            "population",
            "finding_tag",
            "finding_tag_family",
            "reporting",
            "theory_driven",
            "task",
            "stimuli_category",
            "modality",
            "consciousness_measure_phase",
            "consciousness_measure_type",
            "type_of_consciousness",
            "technique",
            "measure"
        }:
            target_url = self.reverse_with_query_params("experiments-graphs-parameters-distribution-bar",
                                                        breakdown=breakdown, theory=self.gnw_parent_theory.id)
            res = self.client.get(target_url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
