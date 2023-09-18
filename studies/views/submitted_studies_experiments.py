import copy
from typing import List, Dict

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from approval_process.choices import ApprovalChoices
from studies.models import Experiment, Paradigm, Technique
from studies.permissions import SubmitterOnlyPermission
from studies.serializers import FullExperimentSerializer, ParadigmSerializer, ParadigmAddRemoveSerializer, \
    TechniqueAddRemoveSerializer, TechniqueSerializer, ThinExperimentSerializer, NoteUpdateSerializer, \
    OptionalNoteUpdateSerializer
from studies.views.base_study_related_views_mixins import StudyRelatedPermissionsViewMixin


class SubmittedStudyExperiments(StudyRelatedPermissionsViewMixin,
                                ModelViewSet,
                                GenericViewSet):
    # TODO handle permissions, so delete/patch can't be done for non draft studies, or none mine
    permission_classes = [SubmitterOnlyPermission]
    pagination_class = None
    serializer_class = FullExperimentSerializer
    queryset = Experiment.objects.select_related("study", "study__approval_process", "study__submitter")

    def get_queryset(self):
        qs = super().get_queryset() \
            .filter(study=self.kwargs.get("study_pk")) \
            .filter(study__submitter=self.request.user)
        if self.action in ["create", "update", "partial_update", "delete"]:
            qs = qs.filter(study__approval_status=ApprovalChoices.PENDING)
        return qs

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ThinExperimentSerializer
        else:
            return super().get_serializer_class()

    @extend_schema(request=ParadigmAddRemoveSerializer())
    @action(detail=True, methods=["POST"], serializer_class=ParadigmSerializer)
    def add_paradigm(self, request, pk, *args, **kwargs):
        serializer = ParadigmAddRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        experiment = self.get_object()
        paradigm = Paradigm.objects.get(id=serializer.validated_data.get("id"))
        experiment.paradigms.add(paradigm)

        res_serializer = ParadigmSerializer(instance=paradigm)
        return Response(res_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=ParadigmAddRemoveSerializer())
    @action(detail=True, methods=["POST"], serializer_class=ParadigmSerializer)
    def remove_paradigm(self, request, pk, *args, **kwargs):
        serializer = ParadigmAddRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        experiment = self.get_object()
        paradigm = Paradigm.objects.get(id=serializer.validated_data.get("id"))
        experiment.paradigms.remove(paradigm)

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=TechniqueAddRemoveSerializer())
    @action(detail=True, methods=["POST"], serializer_class=TechniqueSerializer)
    def add_technique(self, request, pk, *args, **kwargs):
        serializer = TechniqueAddRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        experiment = self.get_object()
        technique = Technique.objects.get(id=serializer.validated_data.get("id"))
        experiment.techniques.add(technique)

        res_serializer = TechniqueSerializer(instance=technique)
        return Response(res_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=TechniqueAddRemoveSerializer())
    @action(detail=True, methods=["POST"], serializer_class=TechniqueSerializer)
    def remove_technique(self, request, pk, *args, **kwargs):
        serializer = TechniqueAddRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        experiment = self.get_object()
        technique = Technique.objects.get(id=serializer.validated_data.get("id"))
        experiment.techniques.remove(technique)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=ThinExperimentSerializer())
    def create(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        data["study"] = int(self.kwargs.get("study_pk"))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)  # validate against the "full serializer"

        experiment = serializer.save()

        # Now we return a full experiment object

        serializer = FullExperimentSerializer(instance=experiment)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(request=ThinExperimentSerializer())
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        experiment = serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        # Now we return a full experiment object

        serializer = FullExperimentSerializer(instance=experiment)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def _set_experiment_note(self, request, note_field: str, is_optional_note: bool = False):
        instance: Experiment = self.get_object()
        serializer = NoteUpdateSerializer(data=request.data)
        if is_optional_note:
            serializer = OptionalNoteUpdateSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        note_text = serializer.validated_data.get("note")
        setattr(instance, note_field, note_text)
        instance.save()
        serializer = self.get_serializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(request=NoteUpdateSerializer())
    @action(detail=True, methods=["POST"], serializer_class=FullExperimentSerializer)
    def set_results_summary_notes(self, request, pk, *args, **kwargs):
        return self._set_experiment_note(request, note_field="results_summary", is_optional_note=False)

    @extend_schema(request=OptionalNoteUpdateSerializer())
    @action(detail=True, methods=["POST"], serializer_class=FullExperimentSerializer)
    def set_tasks_notes(self, request, pk, *args, **kwargs):
        return self._set_experiment_note(request, note_field="tasks_notes", is_optional_note=True)

    @extend_schema(request=OptionalNoteUpdateSerializer())
    @action(detail=True, methods=["POST"], serializer_class=FullExperimentSerializer)
    def set_consciousness_measures_notes(self, request, pk, *args, **kwargs):
        return self._set_experiment_note(request, note_field="consciousness_measures_notes", is_optional_note=True)

    @extend_schema(request=OptionalNoteUpdateSerializer())
    @action(detail=True, methods=["POST"], serializer_class=FullExperimentSerializer)
    def set_stimuli_notes(self, request, pk, *args, **kwargs):
        return self._set_experiment_note(request, note_field="stimuli_notes", is_optional_note=True)

    @extend_schema(request=OptionalNoteUpdateSerializer())
    @action(detail=True, methods=["POST"], serializer_class=FullExperimentSerializer)
    def set_paradigms_notes(self, request, pk, *args, **kwargs):
        return self._set_experiment_note(request, note_field="paradigms_notes", is_optional_note=True)

    @extend_schema(request=OptionalNoteUpdateSerializer())
    @action(detail=True, methods=["POST"], serializer_class=FullExperimentSerializer)
    def set_samples_notes(self, request, pk, *args, **kwargs):
        return self._set_experiment_note(request, note_field="sample_notes", is_optional_note=True)
