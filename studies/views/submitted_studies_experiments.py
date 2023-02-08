import copy
import json
from typing import List, Dict

from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.models import Experiment, Study, Task, Measure
from studies.serializers import FullExperimentSerializer, ExperimentSerializer, TaskSerializer, SampleSerializer, \
    StimulusSerializer, MeasureSerializer, InterpretationSerializer, ConsciousnessMeasureSerializer, \
    FindingTagSerializer


class SubmittedStudyExperiments(mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.UpdateModelMixin,
                                GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FullExperimentSerializer
    queryset = Experiment.objects.select_related("study", "study__approval_process", "study__submitter") \
        .filter(study__approval_status=ApprovalChoices.PENDING)

    def get_queryset(self):
        return super().get_queryset() \
            .filter(study__approval_status=ApprovalChoices.PENDING) \
            .filter(study=self.kwargs.get("study_pk")) \
            .filter(study__submitter=self.request.user)

    def create_nested_objects(self, experiment_id: int, items_data: List[Dict],
                              serializer_cls: ModelSerializer.__class__):
        items_list = [dict(experiment=experiment_id, **item_data) for item_data in items_data]
        related_serializer = serializer_cls(data=items_list, many=True)
        related_serializer.is_valid(raise_exception=True)
        related_serializer.save()

    def create(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        data["study"] = int(self.kwargs.get("study_pk"))
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)  # validate against the "full serializer"

        # Now we move to create the experiment first as nested serializers with many=True don't work with create
        kwargs = dict(data=data)
        kwargs.setdefault('context', self.get_serializer_context())
        experiment_serializer = ExperimentSerializer(**kwargs)
        experiment_serializer.is_valid(raise_exception=True)
        experiment = experiment_serializer.save()

        # Moving to create related objects
        tasks_data = data.pop("tasks")
        self.create_nested_objects(experiment_id=experiment.id, items_data=tasks_data, serializer_cls=TaskSerializer)

        samples_data = data.pop("samples")
        self.create_nested_objects(experiment_id=experiment.id, items_data=samples_data,
                                   serializer_cls=SampleSerializer)

        stimuli_data = data.pop("stimuli")
        self.create_nested_objects(experiment_id=experiment.id, items_data=stimuli_data,
                                   serializer_cls=StimulusSerializer)

        measures_data = data.pop("measures")
        self.create_nested_objects(experiment_id=experiment.id, items_data=measures_data,
                                   serializer_cls=MeasureSerializer)

        interpretations_data = data.pop("interpretations")
        self.create_nested_objects(experiment_id=experiment.id, items_data=interpretations_data,
                                   serializer_cls=InterpretationSerializer)

        consciousness_measures_data = data.pop("consciousness_measures")
        self.create_nested_objects(experiment_id=experiment.id, items_data=consciousness_measures_data,
                                   serializer_cls=ConsciousnessMeasureSerializer)

        finding_tags_data = data.pop("finding_tags")
        self.create_nested_objects(experiment_id=experiment.id, items_data=finding_tags_data,
                                   serializer_cls=FindingTagSerializer)

        # Now get the instance back
        instance = Experiment.objects.get(id=experiment.id)
        serializer = self.get_serializer(instance=instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
