from rest_framework import status

from contrast_api.choices import ReportingChoices, InterpretationsChoices
from contrast_api.tests.base import BaseTestCase
from studies.open_api_parameters import BREAKDOWN_OPTIONS


# Create your tests here.
class ParameterDistributionTheoriesComparisonPieGraphTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def _given_world_setup(self):
        israeli_study = self.given_study_exists(
            title="Israeli study", countries=["IL"], DOI="10.1016/j.cortex.2017.07.011", year=2002
        )
        british_israeli_study = self.given_study_exists(
            title="british", countries=["UK", "IL"], DOI="10.1016/j.cortex.2017.07.012", year=2004
        )
        self.gnw_parent_theory = self.given_theory_exists(parent=None, name="GNW", acronym="GNW")
        self.rpt_parent_theory = self.given_theory_exists(parent=None, name="RPT", acronym="RPT")
        self.gnw_child_theory = self.given_theory_exists(parent=self.gnw_parent_theory, name="GNW_child")
        self.rpt_child_theory = self.given_theory_exists(parent=self.rpt_parent_theory, name="RPT_child")
        masking_parent_paradigm = self.given_paradigm_exists(name="masking_parent_paradigm")
        masking_child_paradigm = self.given_paradigm_exists(
            name="masking_child_paradigm", parent=masking_parent_paradigm
        )
        different_parent_paradigm = self.given_paradigm_exists(name="different_parent_paradigm")
        different_child_paradigm = self.given_paradigm_exists(
            name="different_child_paradigm", parent=different_parent_paradigm
        )
        another_different_child_paradigm = self.given_paradigm_exists(
            name="zz_another_different_child_paradigm", parent=different_parent_paradigm
        )
        first_technique = self.given_technique_exists("a_first_technique")
        second_technique = self.given_technique_exists("b_second_technique")
        israeli_study_experiment = self.given_experiment_exists_for_study(
            study=israeli_study,
            paradigms=[masking_child_paradigm],
            is_reporting=ReportingChoices.NO_REPORT,
            techniques=[second_technique],
        )
        israeli_study_experiment_2 = self.given_experiment_exists_for_study(
            study=israeli_study,
            results_summary="brave new world",
            techniques=[second_technique],
            is_reporting=ReportingChoices.NO_REPORT,
            paradigms=[different_child_paradigm, masking_child_paradigm],
        )
        british_israeli_study_experiment = self.given_experiment_exists_for_study(
            study=british_israeli_study,
            techniques=[first_technique, second_technique],
            is_reporting=ReportingChoices.BOTH,
            paradigms=[masking_child_paradigm, another_different_child_paradigm],
        )
        # setup:
        """
        masking parent paradigm 
         gnw -pro: 2 against: 1
         rpt pro:  1 against: 1
        different parent paradigm - 
         gnw - pro: 1 against: 1
         rpt - pro:1  against: 
        """
        self.given_interpretation_exist(
            experiment=israeli_study_experiment,  # masking_child_paradigm
            theory=self.gnw_child_theory,
            interpretation_type=InterpretationsChoices.PRO,
        )

        self.given_interpretation_exist(
            experiment=british_israeli_study_experiment,
            # masking_child_paradigm, different
            theory=self.gnw_child_theory,
            interpretation_type=InterpretationsChoices.CHALLENGES,
        )

        self.given_interpretation_exist(
            experiment=israeli_study_experiment,  # masking_child_paradigm
            theory=self.rpt_child_theory,
            interpretation_type=InterpretationsChoices.CHALLENGES,
        )

        self.given_interpretation_exist(
            experiment=israeli_study_experiment_2,  # masking_child_paradigm, different
            theory=self.gnw_child_theory,
            interpretation_type=InterpretationsChoices.PRO,
        )

        self.given_interpretation_exist(
            experiment=british_israeli_study_experiment,
            # masking_child_paradigm, different
            theory=self.rpt_child_theory,
            interpretation_type=InterpretationsChoices.PRO,
        )
        first_measure = self.given_measure_exists(
            experiment_id=israeli_study_experiment.id, measure_type="a_first_measure"
        )
        second_measure = self.given_measure_exists(
            experiment_id=israeli_study_experiment.id, measure_type="b_second_measure"
        )
        third_measure_with_second_type = self.given_measure_exists(
            experiment_id=israeli_study_experiment_2.id, measure_type="b_second_measure"
        )
        fourth_measure = self.given_measure_exists(
            experiment_id=british_israeli_study_experiment.id, measure_type="c_third_measure"
        )
        return (
            another_different_child_paradigm,
            different_child_paradigm,
            different_parent_paradigm,
            first_measure,
            first_technique,
            fourth_measure,
            masking_child_paradigm,
            masking_parent_paradigm,
            second_measure,
            second_technique,
            third_measure_with_second_type,
        )

    def test_parameters_distribution_comparison_by_theory_pie_breakdown_paradigm_family(self):
        (
            another_different_child_paradigm,
            different_child_paradigm,
            different_parent_paradigm,
            first_measure,
            first_technique,
            fourth_measure,
            masking_child_paradigm,
            masking_parent_paradigm,
            second_measure,
            second_technique,
            third_measure_with_second_type,
        ) = self._given_world_setup()
        target_url = self.reverse_with_query_params(
            "experiments-graphs-parameters-distribution-theories-comparison",
            breakdown="paradigm_family",
            interpretation=InterpretationsChoices.PRO,
        )
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 2)  # as gnw child interperation to two paradigms
        """
        masking parent paradigm -
         gnw -pro: 2 against: 1
         rpt pro:  1 against: 1
        different parent paradigm - 
         gnw - pro: 1 against: 1
         rpt - pro:1  against: """
        first_series = res.data[0]
        second_series = res.data[1]

        self.assertEqual(first_series["series_name"], self.gnw_parent_theory.name)  # 3 total prod
        self.assertEqual(first_series["value"], 2)  # 2 experiments with GWT and PRO
        self.assertEqual(second_series["series_name"], self.rpt_parent_theory.name)  # 2 pro
        self.assertEqual(second_series["value"], 1)  # 2 pro

        self.assertEqual(first_series["series"][0]["key"], masking_parent_paradigm.name)
        self.assertEqual(first_series["series"][0]["value"], 2)

        self.assertEqual(first_series["series"][1]["key"], different_parent_paradigm.name)
        self.assertEqual(first_series["series"][1]["value"], 1)

    def test_all_options_sanity_test(self):
        """
        This is just a basic sanity test, that nothing throws an exception, later we might add more here
        """
        (
            another_different_child_paradigm,
            different_child_paradigm,
            different_parent_paradigm,
            first_measure,
            first_technique,
            fourth_measure,
            masking_child_paradigm,
            masking_parent_paradigm,
            second_measure,
            second_technique,
            third_measure_with_second_type,
        ) = self._given_world_setup()
        for breakdown in BREAKDOWN_OPTIONS:
            target_url = self.reverse_with_query_params(
                "experiments-graphs-parameters-distribution-theories-comparison",
                breakdown=breakdown,
                interpretation=InterpretationsChoices.PRO,
            )
            res = self.client.get(target_url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
