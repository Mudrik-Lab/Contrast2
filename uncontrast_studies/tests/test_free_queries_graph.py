from rest_framework import status

from contrast_api.choices import StudyTypeChoices, PresentationModeChoices, SignificanceChoices, UnConSampleChoices
from uncontrast_studies.models import UnConSample, UnConStimulusCategory, UnConModalityType
from uncontrast_studies.open_api_parameters import UNCONTRAST_GRAPH_BREAKDOWN_OPTIONS
from uncontrast_studies.tests.base import UnContrastBaseTestCase


class TestFreeQueriesGraphTestCase(UnContrastBaseTestCase):
    def _setup_world(self):
        study = self.given_study_exists(
            title="Israeli study",
            countries=["IL"],
            DOI="10.1016/j.cortex.2017.07.011",
            year=2002,
            type=StudyTypeChoices.UNCONSCIOUSNESS,
        )

        later_study = self.given_study_exists(
            title="british study",
            countries=["UK"],
            DOI="10.1016/j.cortex.2018.07.011",
            year=2010,
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

        sample_1 = dict(type=UnConSampleChoices.CHILDREN, size_included=10, size_excluded=6, size_total=4)
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
        experiment_positive_1 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            study,
            significance=SignificanceChoices.POSITIVE,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            suppressed_stimuli=[suppressed_stimulus_1],
            samples=[sample_1],
            unconsciousness_measures=[unconsciousness_measure_1, unconsciousness_measure_2],
        )

        experiment_positive_2 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            study,
            significance=SignificanceChoices.POSITIVE,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            suppressed_stimuli=[suppressed_stimulus_1, suppressed_stimulus_2],
            samples=[sample_2],
            unconsciousness_measures=[unconsciousness_measure_2],
        )

        experiment_negative_1 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            study,
            significance=SignificanceChoices.NEGATIVE,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            suppressed_stimuli=[suppressed_stimulus_1],
            samples=[sample_1],
            unconsciousness_measures=[unconsciousness_measure_1, unconsciousness_measure_2],
        )

        experiment_negative_2 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            later_study,
            significance=SignificanceChoices.NEGATIVE,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            suppressed_stimuli=[suppressed_stimulus_1, suppressed_stimulus_2],
            samples=[sample_1],
            unconsciousness_measures=[unconsciousness_measure_1],
        )

        experiment_mixed_1 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            study,
            significance=SignificanceChoices.MIXED,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            suppressed_stimuli=[suppressed_stimulus_1],
            samples=[sample_1],
            unconsciousness_measures=[unconsciousness_measure_1, unconsciousness_measure_2],
        )

        experiment_mixed_2 = self.given_uncon_experiment_exists_for_study(  # noqa: F841
            later_study,
            significance=SignificanceChoices.MIXED,  # We override it, although basically it's from findings
            paradigm=specific_paradigm,
            suppressed_stimuli=[suppressed_stimulus_1, suppressed_stimulus_2],
            samples=[sample_1],
            unconsciousness_measures=[unconsciousness_measure_1],
        )

    def test_sanity_breakdown_implementation(self):
        self._setup_world()
        for breakdown in UNCONTRAST_GRAPH_BREAKDOWN_OPTIONS:
            target_url = self.reverse_with_query_params(
                "uncontrast-experiments-graphs-parameters-distribution-free-queries", breakdown=breakdown
            )
            res = self.client.get(target_url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_sanity_filters_implementation(self):
        self._setup_world()
        filter_name = "populations"

        first_sample = UnConSample.objects.first()
        filters = {filter_name: first_sample.id}
        target_url = self.reverse_with_query_params(
            "uncontrast-experiments-graphs-parameters-distribution-free-queries",
            breakdown="modes_of_presentation",
            **filters,
        )
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        filter_name = "are_participants_excluded"

        first_sample = UnConSample.objects.first()
        filters = {filter_name: True}
        target_url = self.reverse_with_query_params(
            "uncontrast-experiments-graphs-parameters-distribution-free-queries",
            breakdown="modes_of_presentation",
            **filters,
        )
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        filter_name = "suppressed_stimuli_categories"
        first_sample = UnConStimulusCategory.objects.first()
        filters = {filter_name: first_sample.id}
        target_url = self.reverse_with_query_params(
            "uncontrast-experiments-graphs-parameters-distribution-free-queries",
            breakdown="modes_of_presentation",
            **filters,
        )
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        filter_name = "target_stimuli_modalities"
        first_sample = UnConModalityType.objects.first()
        filters = {filter_name: first_sample.id}
        target_url = self.reverse_with_query_params(
            "uncontrast-experiments-graphs-parameters-distribution-free-queries",
            breakdown="consciousness_measure_phase",
            **filters,
        )
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
