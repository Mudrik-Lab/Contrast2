import copy
from typing import List, Dict

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from approval_process.choices import ApprovalChoices
from contrast_api.studies.permissions import SubmitterOnlyPermission

from contrast_api.serializers import NoteUpdateSerializer, OptionalNoteUpdateSerializer
from studies.views.base_study_related_views_mixins import StudyRelatedPermissionsViewMixin
from uncontrast_studies.models import UnConExperiment
from uncontrast_studies.serializers import FullUnConExperimentSerializer, ThinUnConExperimentSerializer


class SubmittedUnContrastStudyExperiments(StudyRelatedPermissionsViewMixin, ModelViewSet, GenericViewSet):
    permission_classes = [SubmitterOnlyPermission]
    pagination_class = None
    serializer_class = FullUnConExperimentSerializer
    queryset = UnConExperiment.objects.select_related("study", "study__approval_process", "study__submitter")

    def get_queryset(self):
        qs = super().get_queryset().filter(study=self.kwargs.get("study_pk"))
        is_reviewer = hasattr(self.request.user, "profile") and self.request.user.profile.is_reviewer
        if not is_reviewer:
            # if not a reviewer we do an extra filter here just to be on the safe sid
            qs = qs.filter(study__submitter=self.request.user)
        if self.action in ["create", "update", "partial_update", "delete"]:
            # we can update only non approved studies
            # if it's a reviewer user then they can also update awaiting review docs
            if is_reviewer:
                qs = qs.filter(study__approval_status__in=[ApprovalChoices.PENDING, ApprovalChoices.AWAITING_REVIEW])
            else:
                qs = qs.filter(study__approval_status=ApprovalChoices.PENDING)
        return qs

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ThinUnConExperimentSerializer
        else:
            return super().get_serializer_class()

    @extend_schema(request=ThinUnConExperimentSerializer())
    def create(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        data["study"] = int(self.kwargs.get("study_pk"))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)  # validate against the "full serializer"

        experiment = serializer.save()

        # Now we return a full experiment object

        serializer = FullUnConExperimentSerializer(instance=experiment)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(request=ThinUnConExperimentSerializer())
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        experiment = serializer.save()

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        # Now we return a full experiment object

        serializer = FullUnConExperimentSerializer(instance=experiment)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def _set_experiment_note(self, request, note_field: str, is_optional_note: bool = False):
        instance: UnConExperiment = self.get_object()
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
    @action(detail=True, methods=["POST"], serializer_class=FullUnConExperimentSerializer)
    def set_experiment_findings_notes(self, request, pk, *args, **kwargs):
        return self._set_experiment_note(request, note_field="experiment_findings_notes", is_optional_note=False)

    @extend_schema(request=OptionalNoteUpdateSerializer())
    @action(detail=True, methods=["POST"], serializer_class=FullUnConExperimentSerializer)
    def set_consciousness_measures_notes(self, request, pk, *args, **kwargs):
        return self._set_experiment_note(request, note_field="consciousness_measures_notes", is_optional_note=True)
