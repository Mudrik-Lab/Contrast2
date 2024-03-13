from rest_framework import status

from contrast_api.choices import ReportingChoices, InterpretationsChoices
from studies.models import FindingTagFamily, FindingTagType
from contrast_api.tests.base import BaseTestCase


# Create your tests here.
class FrequenciesGraphTestCase(BaseTestCase):
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
        self.gnw_parent_theory = self.given_theory_exists(parent=None, name="GNW_parent", acronym="GNW")
        self.rpt_parent_theory = self.given_theory_exists(parent=None, name="RPT_parent", acronym="RPT")
        gnw_child_theory = self.given_theory_exists(parent=self.gnw_parent_theory, name="GNW_child")
        rpt_child_theory = self.given_theory_exists(parent=self.rpt_parent_theory, name="RPT_child")
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
        frequency_family = FindingTagFamily.objects.get(name="Frequency")
        tag_type_beta = FindingTagType.objects.create(name="Beta", family=frequency_family)
        tag_type_gamma = FindingTagType.objects.create(name="Gamma", family=frequency_family)
        first_tag_data = dict(
            type=tag_type_beta,
            technique=first_technique,
            family=frequency_family,
            onset=500,
            offset=600,
            band_lower_bound=50,
            band_higher_bound=100,
            is_NCC=True,
        )
        second_tag_data = dict(
            type=tag_type_gamma,
            technique=second_technique,
            family=frequency_family,
            onset=120,
            offset=150,
            band_lower_bound=120,
            band_higher_bound=150,
            is_NCC=True,
        )
        third_tag_data = dict(
            type=tag_type_gamma,
            technique=second_technique,
            family=frequency_family,
            onset=200,
            offset=250,
            band_lower_bound=200,
            band_higher_bound=250,
            is_NCC=True,
        )

        israeli_study_experiment = self.given_experiment_exists_for_study(
            study=israeli_study,
            paradigms=[masking_child_paradigm],
            is_reporting=ReportingChoices.NO_REPORT,
            techniques=[second_technique],
            finding_tags=[third_tag_data],
        )
        israeli_study_experiment_2 = self.given_experiment_exists_for_study(
            study=israeli_study,
            results_summary="brave new world",
            techniques=[second_technique],
            is_reporting=ReportingChoices.NO_REPORT,
            finding_tags=[second_tag_data, third_tag_data],
            paradigms=[different_child_paradigm, masking_child_paradigm],
        )
        british_israeli_study_experiment = self.given_experiment_exists_for_study(
            study=british_israeli_study,
            techniques=[first_technique, second_technique],
            is_reporting=ReportingChoices.BOTH,
            finding_tags=[first_tag_data, third_tag_data],
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
            theory=gnw_child_theory,
            interpretation_type=InterpretationsChoices.PRO,
        )

        self.given_interpretation_exist(
            experiment=british_israeli_study_experiment,
            # masking_child_paradigm, different
            theory=gnw_child_theory,
            interpretation_type=InterpretationsChoices.CHALLENGES,
        )

        self.given_interpretation_exist(
            experiment=israeli_study_experiment,  # masking_child_paradigm
            theory=rpt_child_theory,
            interpretation_type=InterpretationsChoices.CHALLENGES,
        )

        self.given_interpretation_exist(
            experiment=israeli_study_experiment_2,  # masking_child_paradigm, different
            theory=gnw_child_theory,
            interpretation_type=InterpretationsChoices.PRO,
        )

        self.given_interpretation_exist(
            experiment=british_israeli_study_experiment,
            # masking_child_paradigm, different
            theory=rpt_child_theory,
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

    def test_frequencies_basic_implementation(self):
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
            "experiments-graphs-frequencies",
            theory=self.gnw_parent_theory.name,
            techniques=[first_technique.name, second_technique.name],
        )
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 2)  # as gnw child PRO interpretation to two experiments

        first_series = res.data[0]  # supposed to tags of experiment 2 (P300 120, 150)(P300, 200, 250)
        second_series = res.data[1]  # supposed to tags of experiment 1 (P300, 200, 250)

        self.assertEqual(len(first_series["series"]), 2)  # supposed to be second experiment which has two tags
        # Verify order
        self.assertLess(first_series["series"][0]["start"], second_series["series"][0]["start"])
