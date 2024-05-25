from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from configuration.models import GraphImage
from configuration.serializers import (
    StudiesConfigurationSerializer,
    GraphsConfigurationSerializer,
    RegistrationConfigurationSerializer,
    UnConStudiesConfigurationSerializer,
)
from contrast_api.choices import (
    SampleChoices,
    TheoryDrivenChoices,
    ExperimentTypeChoices,
    AALAtlasTagChoices,
    AnalysisTypeChoices,
    DirectionChoices,
    UnConSampleChoices,
    PresentationModeChoices,
)
from studies.models import (
    Study,
    Technique,
    FindingTagType,
    FindingTagFamily,
    MeasureType,
    Theory,
    Paradigm,
    TaskType,
    ConsciousnessMeasureType,
    ConsciousnessMeasurePhaseType,
    Author,
    ModalityType,
    Experiment,
)
from studies.models.stimulus import StimulusCategory, StimulusSubCategory
from uncontrast_studies.models import (
    UnConSpecificParadigm,
    UnConsciousnessMeasurePhase,
    UnConsciousnessMeasureType,
    UnConsciousnessMeasureSubType,
    UnConTaskType,
    UnConModalityType,
    UnConStimulusCategory,
    UnConStimulusSubCategory,
    UnConExperiment,
    UnConProcessingMainDomain,
    UnConMainParadigm,
    UnConSuppressionMethodType,
    UnConSuppressionMethodSubType,
    UnConFinding,
)
from users.choices import GenderChoices, AcademicStageChoices


# Create your views here.


class ConfigurationView(GenericViewSet):
    queryset = Study.objects.none()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == "studies_form":
            return StudiesConfigurationSerializer
        elif self.action == "uncon_studies_form":
            return UnConStudiesConfigurationSerializer
        elif self.action == "graphs":
            return GraphsConfigurationSerializer
        else:
            return super().get_serializer_class()

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=UnConStudiesConfigurationSerializer,
        permission_classes=[AllowAny],
    )
    def uncon_studies_form(self, request, **kwargs):
        existing_journals = (
            Study.objects.values("abbreviated_source_title")
            .order_by("abbreviated_source_title")
            .distinct()
            .values_list("abbreviated_source_title", flat=True)
        )
        available_populations_types = UnConSampleChoices.values
        available_mode_of_presentation = PresentationModeChoices.values
        available_consciousness_measure_phase_type = UnConsciousnessMeasurePhase.objects.all()
        available_consciousness_measure_type = UnConsciousnessMeasureType.objects.all()
        available_consciousness_measure_sub_type = UnConsciousnessMeasureSubType.objects.all()
        available_tasks_types = UnConTaskType.objects.all()
        available_suppression_method_types = UnConSuppressionMethodType.objects.all()
        available_suppression_method_sub_types = UnConSuppressionMethodSubType.objects.all()
        available_processing_main_domain_types = UnConProcessingMainDomain.objects.all()
        available_specific_paradigm_type = UnConSpecificParadigm.objects.all()
        available_main_paradigm_type = UnConMainParadigm.objects.all()
        available_authors = Author.objects.all()
        available_stimulus_modality_type = UnConModalityType.objects.all()
        available_stimulus_category_type = UnConStimulusCategory.objects.all()
        available_stimulus_sub_category_type = UnConStimulusSubCategory.objects.all()
        available_outcomes_type = UnConFinding.objects.values_list("outcome", flat=True).distinct()
        available_experiment_types = [dict(name=v, value=k) for k, v in ExperimentTypeChoices.choices]
        are_participants_excluded_options = [True, False]
        is_trial_excluded_based_on_measure_options = [True, False]
        approved_experiments_count = UnConExperiment.objects.filter(
            study__approval_status=ApprovalChoices.APPROVED
        ).count()

        configuration_data = dict(
            existing_journals=existing_journals,
            available_populations_types=available_populations_types,
            available_mode_of_presentation=available_mode_of_presentation,
            available_experiment_types=available_experiment_types,
            available_consciousness_measure_phase_type=available_consciousness_measure_phase_type,
            available_consciousness_measure_type=available_consciousness_measure_type,
            available_consciousness_measure_sub_type=available_consciousness_measure_sub_type,
            available_authors=available_authors,
            available_stimulus_modality_type=available_stimulus_modality_type,
            available_stimulus_category_type=available_stimulus_category_type,
            available_stimulus_sub_category_type=available_stimulus_sub_category_type,
            available_tasks_types=available_tasks_types,
            available_suppression_method_types=available_suppression_method_types,
            available_suppression_method_sub_types=available_suppression_method_sub_types,
            available_processing_main_domain_types=available_processing_main_domain_types,
            available_specific_paradigm_type=available_specific_paradigm_type,
            available_main_paradigm_type=available_main_paradigm_type,
            available_outcomes_type=available_outcomes_type,
            is_trial_excluded_based_on_measure_options=is_trial_excluded_based_on_measure_options,
            are_participants_excluded_options=are_participants_excluded_options,
            approved_experiments_count=approved_experiments_count,
        )

        serializer = self.get_serializer(instance=configuration_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["GET"], serializer_class=StudiesConfigurationSerializer, permission_classes=[AllowAny]
    )
    def studies_form(self, request, **kwargs):
        existing_journals = (
            Study.objects.values("abbreviated_source_title")
            .order_by("abbreviated_source_title")
            .distinct()
            .values_list("abbreviated_source_title", flat=True)
        )
        techniques = Technique.objects.all()
        available_finding_tags_types = FindingTagType.objects.all().select_related()
        available_finding_tags_families = FindingTagFamily.objects.all()
        available_measure_types = MeasureType.objects.all()
        available_theories = Theory.objects.filter(parent__isnull=False).select_related("parent")
        available_paradigms = Paradigm.objects.filter(parent__isnull=False).select_related("parent", "parent__parent")
        available_paradigms_families = Paradigm.objects.filter(parent__isnull=True)
        available_populations_types = SampleChoices.values
        available_theory_driven_types = TheoryDrivenChoices.values
        available_AAL_atlas_tag_types = AALAtlasTagChoices.values
        available_analysis_type_choices = AnalysisTypeChoices.values
        available_direction_choices = DirectionChoices.values
        available_consciousness_measure_phase_type = ConsciousnessMeasurePhaseType.objects.all()
        available_analysis_measure_type = ConsciousnessMeasureType.objects.all()
        available_tasks_types = TaskType.objects.all()
        available_authors = Author.objects.all()
        available_stimulus_modality_type = ModalityType.objects.all()
        available_stimulus_category_type = StimulusCategory.objects.all()
        available_stimulus_sub_category_type = StimulusSubCategory.objects.all()

        available_experiment_types = [dict(name=v, value=k) for k, v in ExperimentTypeChoices.choices]
        approved_experiments_count = Experiment.objects.filter(study__approval_status=ApprovalChoices.APPROVED).count()
        configuration_data = dict(
            existing_journals=existing_journals,
            available_techniques=techniques,
            available_paradigms_families=available_paradigms_families,
            available_populations_types=available_populations_types,
            available_theory_driven_types=available_theory_driven_types,
            available_AAL_atlas_tag_types=available_AAL_atlas_tag_types,
            available_analysis_type_choices=available_analysis_type_choices,
            available_direction_choices=available_direction_choices,
            available_experiment_types=available_experiment_types,
            available_finding_tags_types=available_finding_tags_types,
            available_finding_tags_families=available_finding_tags_families,
            available_measure_types=available_measure_types,
            available_theories=available_theories,
            available_paradigms=available_paradigms,
            available_consciousness_measure_phase_type=available_consciousness_measure_phase_type,
            available_consciousness_measure_type=available_analysis_measure_type,
            available_analysis_measure_type=available_analysis_measure_type,
            available_authors=available_authors,
            available_stimulus_modality_type=available_stimulus_modality_type,
            available_stimulus_category_type=available_stimulus_category_type,
            available_stimulus_sub_category_type=available_stimulus_sub_category_type,
            available_tasks_types=available_tasks_types,
            approved_experiments_count=approved_experiments_count,
        )

        serializer = self.get_serializer(instance=configuration_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["GET"], serializer_class=GraphsConfigurationSerializer, permission_classes=[AllowAny]
    )
    def graphs(self, request, **kwargs):
        images = GraphImage.objects.all()
        available_parent_theories = (
            Theory.objects.select_related().filter(parent__isnull=True).values_list("name", flat=True)
        )
        available_finding_tags_types_for_timings = FindingTagType.objects.filter(family__name="Temporal").values_list(
            "name", flat=True
        )
        available_techniques_for_frequencies = (
            Technique.objects.filter(findings_tags__family__name="Frequency").distinct().values_list("name", flat=True)
        )
        available_techniques_for_timings = (
            Technique.objects.filter(findings_tags__family__name="Temporal").distinct().values_list("name", flat=True)
        )

        configuration_data = dict(
            images=images,
            available_parent_theories=available_parent_theories,
            available_finding_tags_types_for_timings=available_finding_tags_types_for_timings,
            available_techniques_for_frequencies=available_techniques_for_frequencies,
            available_techniques_for_timings=available_techniques_for_timings,
        )
        serializer = self.get_serializer(instance=configuration_data)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["GET"],
        serializer_class=RegistrationConfigurationSerializer,
        permission_classes=[AllowAny],
    )
    def registration_form(self, request, **kwargs):
        configuration_data = dict(
            gender_options=GenderChoices.values, academic_stage_options=AcademicStageChoices.values
        )
        serializer = self.get_serializer(instance=configuration_data)

        return Response(serializer.data, status=status.HTTP_200_OK)
