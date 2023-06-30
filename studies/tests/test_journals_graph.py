from rest_framework import status

from studies.choices import ReportingChoices, InterpretationsChoices
from contrast_api.tests.base import BaseTestCase


# Create your tests here.
class JournalsGraphTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def _given_world_setup(self):
        self.israeli_study = self.given_study_exists(title="Israeli study", countries=["IL"],
                                                     abbreviated_source_title="the first journal",
                                                DOI="10.1016/j.cortex.2017.07.011", year=2002)
        self.british_israeli_study = self.given_study_exists(title="british", countries=["UK", "IL"],
                                                             abbreviated_source_title="the second journal",
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
        israeli_study_experiment = self.given_experiment_exists_for_study(study=self.israeli_study,
                                                                          paradigms=[masking_child_paradigm],
                                                                          is_reporting=ReportingChoices.NO_REPORT,
                                                                          techniques=[second_technique])
        israeli_study_experiment_2 = self.given_experiment_exists_for_study(study=self.israeli_study,
                                                                            finding_description="brave new world",
                                                                            techniques=[second_technique],
                                                                            is_reporting=ReportingChoices.NO_REPORT,
                                                                            paradigms=[different_child_paradigm,
                                                                                       masking_child_paradigm])
        british_israeli_study_experiment = self.given_experiment_exists_for_study(study=self.british_israeli_study,
                                                                                  techniques=[first_technique,
                                                                                              second_technique],
                                                                                  is_reporting=ReportingChoices.BOTH,
                                                                                  paradigms=[

                                                                                      another_different_child_paradigm])
        self.given_interpretation_exist(experiment=israeli_study_experiment,
                                        theory=gnw_child_theory, interpretation_type=InterpretationsChoices.PRO)

        # this is expected not to be counted
        self.given_interpretation_exist(experiment=israeli_study_experiment,
                                        theory=rpt_child_theory, interpretation_type=InterpretationsChoices.CHALLENGES)

        self.given_interpretation_exist(experiment=israeli_study_experiment_2,
                                        theory=gnw_child_theory, interpretation_type=InterpretationsChoices.PRO)

        self.given_interpretation_exist(experiment=british_israeli_study_experiment,
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

    def test_journals_by_theory(self):
        another_different_child_paradigm, \
        different_child_paradigm, \
        different_parent_paradigm, \
        first_measure, first_technique, \
        fourth_measure, masking_child_paradigm, \
        masking_parent_paradigm, second_measure, \
        second_technique, third_measure_with_second_type = self._given_world_setup()
        target_url = self.reverse_with_query_params("experiments-graphs-journals",
                                                    theory=self.gnw_parent_theory.id)
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1) # as only one study with this interpertation as pro
        first_result = res.data[0]
        self.assertEqual(first_result["key"], "the first journal")
        self.assertEqual(first_result["value"], 2) #two experiments

        # Now check for another theory, rememebr we query by PARENT theory, of the actual theories connected
        target_url = self.reverse_with_query_params("experiments-graphs-journals",
                                                    theory=self.rpt_parent_theory.id)
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # as only one study with this interpertation as pro
        first_result = res.data[0]
        self.assertEqual(first_result["key"], "the second journal")
        self.assertEqual(first_result["value"], 1)  # one experiment

    def test_journals_by_theory_family_data(self):
        """

        """
        israeli_study = self.given_study_exists(title="Israeli study", countries=["IL"],
                                                DOI="10.1016/j.cortex.2017.07.011", year=2002)
        british_israeli_study = self.given_study_exists(title="british", countries=["UK", "IL"],
                                                        DOI="10.1016/j.cortex.2017.07.012", year=2004)
        gnw_parent_theory = self.given_theory_exists(parent=None, name="GNW")
        rpt_parent_theory = self.given_theory_exists(parent=None, name="RPT")
        self.given_theory_exists(parent=gnw_parent_theory, name="GNW_child")
        self.given_theory_exists(parent=rpt_parent_theory, name="RPT_child")
        self.given_experiment_exists_for_study(study=israeli_study,
                                                                          is_reporting=ReportingChoices.NO_REPORT)
        self.given_experiment_exists_for_study(study=israeli_study,
                                                                            finding_description="brave new world",
                                                                            is_reporting=ReportingChoices.NO_REPORT)
        self.given_experiment_exists_for_study(study=british_israeli_study,
                                                                                  is_reporting=ReportingChoices.BOTH,
                                                                                    )

