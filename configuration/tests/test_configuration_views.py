from rest_framework import status

from contrast_api.tests.base import BaseTestCase
from contrast_api.choices import ReportingChoices, InterpretationsChoices
from studies.models import FindingTagFamily, FindingTagType


class ConfigurationViewsTestCase(BaseTestCase):
    def setUp(self) -> None:
        self.given_world_setup()

    def given_world_setup(self):
        israeli_study = self.given_study_exists(
            title="Israeli study", countries=["IL"], DOI="10.1016/j.cortex.2017.07.011", year=2002
        )
        british_israeli_study = self.given_study_exists(
            title="british", countries=["UK", "IL"], DOI="10.1016/j.cortex.2017.07.012", year=2004
        )
        self.gnw_parent_theory = self.given_theory_exists(parent=None, name="GNW", acronym="GNW")
        self.rpt_parent_theory = self.given_theory_exists(parent=None, name="RPT", acronym="RPT")
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
        temporal_family = FindingTagFamily.objects.get(name="Temporal")
        tag_type_N400 = FindingTagType.objects.create(name="N400", family=temporal_family)
        tag_type_P300 = FindingTagType.objects.create(name="P300", family=temporal_family)
        first_tag_data = dict(
            type=tag_type_N400, technique=first_technique, family=temporal_family, onset=100, offset=150, is_NCC=True
        )
        second_tag_data = dict(
            type=tag_type_P300, technique=second_technique, family=temporal_family, onset=120, offset=150, is_NCC=True
        )
        third_tag_data = dict(
            type=tag_type_P300, technique=second_technique, family=temporal_family, onset=200, offset=250, is_NCC=True
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

    def test_configuration_studies_endpoint(self):
        url = self.reverse_with_query_params("configuration-studies-form")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_configuration_uncontrast_studies_endpoint(self):
        url = self.reverse_with_query_params("configuration-uncon-studies-form")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_configuration_graphs_endpoint(self):
        url = self.reverse_with_query_params("configuration-graphs")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("available_parent_theories_including_all", res.data)
        self.assertIn("ALL", res.data["available_parent_theories_including_all"])

    def test_configuration_registration_form_endpoint(self):
        url = self.reverse_with_query_params("configuration-registration-form")
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
