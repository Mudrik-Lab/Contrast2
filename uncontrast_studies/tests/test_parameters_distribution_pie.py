from rest_framework import status

from contrast_api.choices import StudyTypeChoices, PresentationModeChoices, SignificanceChoices, UnConSampleChoices
from uncontrast_studies.open_api_parameters import UNCONTRAST_GRAPH_BREAKDOWN_OPTIONS
from uncontrast_studies.tests.base import UnContrastBaseTestCase


class TestParametersDistributionPieGraphTestCase(UnContrastBaseTestCase):
    def _setup_world(self):
        study = self.given_study_exists(
            title="Israeli study",
            countries=["IL"],
            DOI="10.1016/j.cortex.2017.07.011",
            year=2002,
            type=StudyTypeChoices.UNCONSCIOUSNESS,
        )
        main_paradigm = self.given_uncon_main_paradigm_exists("main_paradigm")
        specific_paradigm = self.given_uncon_specific_paradigm_exists("specific_paradigm", main=main_paradigm)
        stimulus_modality_type = self.given_uncon_stimulus_modality_type_exists("modality_type")
        stimulus_category_type = self.given_uncon_stimulus_category_type_exists("category_type")
        unconsciousness_measure_phase = self.given_unconsciousness_measure_phase_exists("phase_type")
        unconsciousness_measure_category_type = self.given_unconsciousness_measure_category_type_exists("category_type")
        unconsciousness_measure_category_sub_type = self.given_unconsciousness_measure_category_sub_type_exists(
            "category_sub_type", category_type=unconsciousness_measure_category_type
        )
        subjective_measure_type = self.given_unconsciousness_measure_category_type_exists("Subjective")
        objective_measure_type = self.given_unconsciousness_measure_category_type_exists("Objective")
        subjective_measure_sub_type = self.given_unconsciousness_measure_category_sub_type_exists(
            name="Dichotomous", category_type=subjective_measure_type
        )
        objective_measure_sub_type = self.given_unconsciousness_measure_category_sub_type_exists(
            name="Location", category_type=objective_measure_type
        )

        suppressed_stimulus_1 = dict(
            category=stimulus_category_type,
            modality=stimulus_modality_type,
            duration=10,
            number_of_stimuli=5,
            soa=100,
            mode_of_presentation=PresentationModeChoices.LIMINAL,
        )
        suppressed_stimulus_2 = dict(
            category=stimulus_category_type,
            modality=stimulus_modality_type,
            duration=20,
            number_of_stimuli=10,
            soa=100,
            mode_of_presentation=PresentationModeChoices.SUBLIMINAL,
        )

        sample_1 = dict(type=UnConSampleChoices.HEALTHY_CHILDREN, size_included=10, size_excluded=6, size_total=4)
        sample_2 = dict(type=UnConSampleChoices.HEALTHY_ADULTS, size_included=20, size_excluded=8, size_total=12)
        unconsciousness_measure_1 = dict(
            phase=unconsciousness_measure_phase,
            type=unconsciousness_measure_category_type,
            sub_type=unconsciousness_measure_category_sub_type,
            number_of_trials=5,
            number_of_participants_in_awareness_test=20,
            is_cm_same_participants_as_task=True,
            is_performance_above_chance=True,
            is_trial_excluded_based_on_measure=False,
        )
        unconsciousness_measure_2 = dict(
            phase=unconsciousness_measure_phase,
            type=unconsciousness_measure_category_type,
            sub_type=unconsciousness_measure_category_sub_type,
            number_of_trials=8,
            number_of_participants_in_awareness_test=30,
            is_cm_same_participants_as_task=True,
            is_performance_above_chance=True,
            is_trial_excluded_based_on_measure=False,
        )
        unconsciousness_measure_objective = dict(
            phase=unconsciousness_measure_phase,
            type=objective_measure_type,
            sub_type=objective_measure_sub_type,
            number_of_trials=8,
            number_of_participants_in_awareness_test=30,
            is_cm_same_participants_as_task=True,
            is_performance_above_chance=True,
            is_trial_excluded_based_on_measure=False,
        )
        unconsciousness_measure_subjective = dict(
            phase=unconsciousness_measure_phase,
            type=subjective_measure_type,
            sub_type=subjective_measure_sub_type,
            number_of_trials=8,
            number_of_participants_in_awareness_test=30,
            is_cm_same_participants_as_task=True,
            is_performance_above_chance=True,
            is_trial_excluded_based_on_measure=False,
        )
        experiment_positive_1 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            study,
            significance=SignificanceChoices.POSITIVE,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            experiment_findings_notes="experiment_positive_1",
            suppressed_stimuli=[suppressed_stimulus_1],
            samples=[sample_1],
            unconsciousness_measures=[
                unconsciousness_measure_1,
                unconsciousness_measure_2,
                unconsciousness_measure_objective,
                unconsciousness_measure_subjective,
            ],
        )

        experiment_positive_2 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            study,
            significance=SignificanceChoices.POSITIVE,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            experiment_findings_notes="experiment_positive_2",
            suppressed_stimuli=[suppressed_stimulus_1, suppressed_stimulus_2],
            samples=[sample_2],
            unconsciousness_measures=[unconsciousness_measure_2, unconsciousness_measure_objective],
        )

        experiment_negative_1 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            study,
            significance=SignificanceChoices.NEGATIVE,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            experiment_findings_notes="experiment_negative_1",
            suppressed_stimuli=[suppressed_stimulus_1],
            samples=[sample_1],
            unconsciousness_measures=[unconsciousness_measure_1, unconsciousness_measure_2],
        )

        experiment_negative_2 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            study,
            significance=SignificanceChoices.NEGATIVE,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            experiment_findings_notes="experiment_negative_2",
            suppressed_stimuli=[suppressed_stimulus_1, suppressed_stimulus_2],
            samples=[sample_1],
            unconsciousness_measures=[unconsciousness_measure_1],
        )

        experiment_mixed_1 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            study,
            significance=SignificanceChoices.MIXED,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            experiment_findings_notes="experiment_mixed_1",
            suppressed_stimuli=[suppressed_stimulus_1],
            samples=[sample_1],
            unconsciousness_measures=[unconsciousness_measure_1, unconsciousness_measure_2],
        )

        experiment_mixed_2 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            study,
            significance=SignificanceChoices.MIXED,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            experiment_findings_notes="experiment_mixed_2",
            suppressed_stimuli=[suppressed_stimulus_1, suppressed_stimulus_2],
            samples=[sample_1],
            unconsciousness_measures=[unconsciousness_measure_1],
        )

    def test_both_measure_behavior(self):
        self._setup_world()
        target_url = self.reverse_with_query_params(
            "uncontrast-experiments-graphs-parameters-distribution-pie", breakdown="consciousness_measure_type"
        )
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        bars = res.data
        series_name = [bar["series_name"] for bar in bars]

        self.assertEqual(
            len(bars), 3, f"Expected 3 but got {series_name}"
        )  # should be "both", "objective", "category_type"

    def test_sanity_implementation(self):
        self._setup_world()
        for breakdown in UNCONTRAST_GRAPH_BREAKDOWN_OPTIONS:
            target_url = self.reverse_with_query_params(
                "uncontrast-experiments-graphs-parameters-distribution-pie", breakdown=breakdown
            )
            res = self.client.get(target_url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            for bar in res.data:
                try:
                    self.assertLessEqual(
                        len(bar["series"]), 3
                    )  # 3 significance options, but not all might exist for each permutation
                    for series in bar["series"]:
                        self.assertIn(series["key"], SignificanceChoices.labels)
                except AssertionError as e:
                    raise AssertionError(f"for series name {bar['series_name']}") from e
