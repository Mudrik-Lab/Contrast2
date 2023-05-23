from rest_framework import status

from studies.choices import ReportingChoices
from contrast_api.tests.base import BaseTestCase


# Create your tests here.
class AcrossTheYearsGraphTestCase(BaseTestCase):
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
                                                                            finding_description="brave new world",
                                                                            techniques=[second_technique],
                                                                            is_reporting=ReportingChoices.NO_REPORT,
                                                                            paradigms=[different_child_paradigm,
                                                                                       masking_child_paradigm])
        british_israeli_study_experiment = self.given_experiment_exists_for_study(study=british_israeli_study,
                                                                                  techniques=[first_technique,
                                                                                              second_technique],
                                                                                  is_reporting=ReportingChoices.BOTH,
                                                                                  paradigms=[

                                                                                      another_different_child_paradigm])
        first_measure = self.given_measure_exists(experiment_id=israeli_study_experiment.id,
                                                  measure_type="a_first_measure")
        second_measure = self.given_measure_exists(experiment_id=israeli_study_experiment.id,
                                                   measure_type="b_second_measure")
        third_measure_with_second_type = self.given_measure_exists(experiment_id=israeli_study_experiment_2.id,
                                                                   measure_type="b_second_measure")
        fourth_measure = self.given_measure_exists(experiment_id=british_israeli_study_experiment.id,
                                                   measure_type="c_third_measure")
        return another_different_child_paradigm, different_child_paradigm, different_parent_paradigm, first_measure, first_technique, fourth_measure, masking_child_paradigm, masking_parent_paradigm, second_measure, second_technique, third_measure_with_second_type

    def test_across_the_years_breakdown_paradigm_family(self):
        another_different_child_paradigm, \
        different_child_paradigm, \
        different_parent_paradigm, \
        first_measure, first_technique, \
        fourth_measure, masking_child_paradigm, \
        masking_parent_paradigm, second_measure, \
        second_technique, third_measure_with_second_type = self._given_world_setup()
        target_url = self.reverse_with_query_params("experiments-graphs-across-the-years",
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
        self.assertDictEqual(first_series["series"][1], dict(year=2004, value=2))  # accumulated

    def test_across_the_years_breakdown_paradigm(self):
        another_different_child_paradigm, \
        different_child_paradigm, \
        different_parent_paradigm, \
        first_measure, first_technique, \
        fourth_measure, masking_child_paradigm, \
        masking_parent_paradigm, second_measure, \
        second_technique, third_measure_with_second_type = self._given_world_setup()
        target_url = self.reverse_with_query_params("experiments-graphs-across-the-years",
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
        self.assertDictEqual(third_series["series"][0], dict(year=2002, value=0))
        self.assertDictEqual(third_series["series"][1], dict(year=2004, value=1))

    def test_across_the_years_breakdown_measures(self):
        another_different_child_paradigm, \
        different_child_paradigm, \
        different_parent_paradigm, \
        first_measure, first_technique, \
        fourth_measure, masking_child_paradigm, \
        masking_parent_paradigm, second_measure, \
        second_technique, third_measure_with_second_type = self._given_world_setup()
        target_url = self.reverse_with_query_params("experiments-graphs-across-the-years",
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
        self.assertDictEqual(third_series["series"][0], dict(year=2002, value=0)) # filler for start year
        self.assertDictEqual(third_series["series"][1], dict(year=2004, value=1))

    def test_across_the_years_techniques_breakdown(self):
        another_different_child_paradigm, \
        different_child_paradigm, \
        different_parent_paradigm, \
        first_measure, first_technique, \
        fourth_measure, masking_child_paradigm, \
        masking_parent_paradigm, second_measure, \
        second_technique, third_measure_with_second_type = self._given_world_setup()

        target_url = self.reverse_with_query_params("experiments-graphs-across-the-years",
                                                    breakdown="technique")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        first_series = res.data[0]
        second_series = res.data[1]

        self.assertEqual(first_series["series_name"], first_technique.name)
        self.assertEqual(second_series["series_name"], second_technique.name)
        # second measure type happened twice
        self.assertDictEqual(first_series["series"][0], dict(year=2002, value=0)) #filler for missing year
        self.assertDictEqual(first_series["series"][1], dict(year=2004, value=1))
        self.assertDictEqual(second_series["series"][0], dict(year=2002, value=2))
        self.assertDictEqual(second_series["series"][1], dict(year=2004, value=3))  # accumulated

    def test_across_the_years_is_reporting_breakdown(self):
        another_different_child_paradigm, \
        different_child_paradigm, \
        different_parent_paradigm, \
        first_measure, first_technique, \
        fourth_measure, masking_child_paradigm, \
        masking_parent_paradigm, second_measure, \
        second_technique, third_measure_with_second_type = self._given_world_setup()

        target_url = self.reverse_with_query_params("experiments-graphs-across-the-years",
                                                    breakdown="reporting")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        first_series = res.data[0]
        second_series = res.data[1]

        self.assertEqual(first_series["series_name"], ReportingChoices.BOTH)
        self.assertEqual(second_series["series_name"], ReportingChoices.NO_REPORT)

        # second measure type happened twice
        self.assertDictEqual(first_series["series"][0], dict(year=2002, value=0))
        self.assertDictEqual(first_series["series"][1], dict(year=2004, value=1))
        self.assertDictEqual(second_series["series"][0], dict(year=2002, value=2))
