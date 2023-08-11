import copy
from typing import List, Dict

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.models import Experiment, Paradigm, Technique, Interpretation
from studies.permissions import SubmitterOnlyPermission
from studies.serializers import FullExperimentSerializer, ParadigmSerializer, ParadigmAddRemoveSerializer, \
    TechniqueAddRemoveSerializer, TechniqueSerializer, ThinExperimentSerializer, InterpretationCreateSerializer
from studies.views.base_study_related_views_mixins import StudyRelatedPermissionsViewMixin


class SubmittedStudyExperiments(StudyRelatedPermissionsViewMixin,
                                mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
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
        experiment = Experiment.objects.get(id=pk)
        paradigm = Paradigm.objects.get(id=serializer.validated_data.get("id"))
        experiment.paradigms.add(paradigm)

        res_serializer = ParadigmSerializer(instance=paradigm)
        return Response(res_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=InterpretationCreateSerializer(many=True))
    @action(detail=True, methods=["POST"], serializer_class=InterpretationCreateSerializer(many=True))
    def setup_interpretations(self, request, pk, *args, **kwargs):
        data = copy.deepcopy(request.data)
        experiment = Experiment.objects.get(id=pk)

        Interpretation.objects.filter(experiment=experiment).delete()
        for item in data:
            item["experiment"] = pk
        serializer = InterpretationCreateSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=ParadigmAddRemoveSerializer())
    @action(detail=True, methods=["POST"], serializer_class=ParadigmSerializer)
    def remove_paradigm(self, request, pk, *args, **kwargs):
        serializer = ParadigmAddRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        experiment = Experiment.objects.get(id=pk)
        paradigm = Paradigm.objects.get(id=serializer.validated_data.get("id"))
        experiment.paradigms.remove(paradigm)

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(request=TechniqueAddRemoveSerializer())
    @action(detail=True, methods=["POST"], serializer_class=TechniqueSerializer)
    def add_technique(self, request, pk, *args, **kwargs):
        serializer = TechniqueAddRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        experiment = Experiment.objects.get(id=pk)
        technique = Technique.objects.get(id=serializer.validated_data.get("id"))
        experiment.techniques.add(technique)

        res_serializer = TechniqueSerializer(instance=technique)
        return Response(res_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=TechniqueAddRemoveSerializer())
    @action(detail=True, methods=["POST"], serializer_class=TechniqueSerializer)
    def remove_technique(self, request, pk, *args, **kwargs):
        serializer = TechniqueAddRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        experiment = Experiment.objects.get(id=pk)
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
