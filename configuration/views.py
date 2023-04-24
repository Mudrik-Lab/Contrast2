from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from configuration.models import GraphImages
from configuration.serializers import StudiesConfigurationSerializer, GraphsConfigurationSerializer
from studies.models import Study, Technique, FindingTagType, FindingTagFamily, MeasureType, Theory, Paradigm, TaskType, \
    ConsciousnessMeasureType, ConsciousnessMeasurePhaseType, Author, ModalityType
from studies.models.stimulus import StimulusCategory, StimulusSubCategory


# Create your views here.


class ConfigurationView(GenericViewSet):
    queryset = Study.objects.none()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == "studies_form":
            return StudiesConfigurationSerializer
        elif self.action == "graphs":
            return GraphsConfigurationSerializer
        else:
            return super().get_serializer_class()

    @action(detail=False, methods=["GET"], serializer_class=StudiesConfigurationSerializer,
            permission_classes=[AllowAny])
    def studies_form(self, request, **kwargs):
        techniques = Technique.objects.all().values_list("name", flat=True)
        available_finding_tags_types = FindingTagType.objects.all()
        available_finding_tags_families = FindingTagFamily.objects.all().values_list("name", flat=True)
        available_measure_types = list(MeasureType.objects.all().values_list("name", flat=True))
        available_theories = Theory.objects.filter(parent__isnull=False)
        available_paradigms = Paradigm.objects.all()
        available_consciousness_measure_phase_type = list(ConsciousnessMeasurePhaseType.objects.all()
                                                          .values_list("name", flat=True))
        available_consciousness_measure_type = list(
            ConsciousnessMeasureType.objects.all().values_list("name", flat=True))
        available_tasks_types = list(TaskType.objects.all().values_list("name", flat=True))
        available_authors = list(Author.objects.all().values_list("name", flat=True))
        available_stimulus_modality_type = list(ModalityType.objects.all().values_list("name", flat=True))
        available_stimulus_category_type = list(StimulusCategory.objects.all().values_list("name", flat=True))
        available_stimulus_sub_category_type = StimulusSubCategory.objects.all()
        configuration_data = dict(available_techniques=techniques,
                                  available_finding_tags_types=available_finding_tags_types,
                                  available_finding_tags_families=available_finding_tags_families,
                                  available_measure_types=available_measure_types,
                                  available_theories=available_theories,
                                  available_paradigms=available_paradigms,
                                  available_consciousness_measure_phase_type=available_consciousness_measure_phase_type,
                                  available_consciousness_measure_type=available_consciousness_measure_type,
                                  available_authors=available_authors,
                                  available_stimulus_modality_type=available_stimulus_modality_type,
                                  available_stimulus_category_type=available_stimulus_category_type,
                                  available_stimulus_sub_category_type=available_stimulus_sub_category_type,
                                  available_tasks_types=available_tasks_types)

        serializer = self.get_serializer(instance=configuration_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], serializer_class=GraphsConfigurationSerializer,
            permission_classes=[AllowAny])
    def graphs(self, request, **kwargs):
        images = GraphImages.objects.all()
        available_parent_theories = Theory.objects.filter(parent__isnull=True).values_list("name", flat=True)
        available_finding_tags_types_for_timings = FindingTagType.objects.filter(family__name="Temporal").values_list(
            "name", flat=True)
        available_techniques_for_frequencies = Technique.objects.filter(
            findings_tags__family__name="Frequency").distinct().values_list("name", flat=True)
        available_techniques_for_timings = Technique.objects.filter(findings_tags__family__name="Temporal").distinct()\
            .values_list("name", flat=True)

        configuration_data = dict(
            images=images,
            available_parent_theories=available_parent_theories,
            available_finding_tags_types_for_timings=available_finding_tags_types_for_timings,
            available_techniques_for_frequencies=available_techniques_for_frequencies,
            available_techniques_for_timings=available_techniques_for_timings,

        )
        serializer = self.get_serializer(instance=configuration_data)

        return Response(serializer.data, status=status.HTTP_200_OK)
