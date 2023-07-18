import copy
from typing import List, Dict

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.choices import ReportingChoices, TheoryDrivenChoices, ExperimentTypeChoices
from studies.models import Experiment, Study
from studies.permissions import SubmitterOnlyPermission
from studies.serializers import FullExperimentSerializer, ExperimentSerializer, TaskSerializer, SampleSerializer, \
    StimulusSerializer, MeasureSerializer, ConsciousnessMeasureSerializer, \
    FindingTagSerializer, InterpretationCreateSerializer


class SubmittedStudyExperiments(mixins.RetrieveModelMixin,
                                mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                GenericViewSet):
    # TODO handle permissions, so delete/patch can't be done for non draft studies, or none mine
    permission_classes = [SubmitterOnlyPermission]
    serializer_class = FullExperimentSerializer
    queryset = Experiment.objects.select_related("study", "study__approval_process", "study__submitter")

    def initial(self, request, *args, **kwargs):
        self.parent_object = get_object_or_404(Study.objects.filter(approval_status=ApprovalChoices.PENDING),
                                               id=self.kwargs["study_pk"])
        return super().initial(request, args, kwargs)

    def check_permissions(self, request):
        # we need to verify it has permissions on the parent object, the study
        super().check_permissions(request)
        super().check_object_permissions(request, self.parent_object)

    def get_queryset(self):
        qs = super().get_queryset() \
            .filter(study=self.kwargs.get("study_pk")) \
            .filter(study__submitter=self.request.user)
        if self.action in ["create", "update", "partial_update", "delete"]:
            qs = qs.filter(study__approval_status=ApprovalChoices.PENDING)
        return qs

    def create_nested_objects(self, experiment_id: int, items_data: List[Dict],
                              serializer_cls: ModelSerializer.__class__):
        items_list = [dict(experiment=experiment_id, **item_data) for item_data in items_data]
        related_serializer = serializer_cls(data=items_list, many=True)
        related_serializer.is_valid(raise_exception=True)
        related_serializer.save()

    @extend_schema(parameters=[OpenApiParameter(name='tasks', type=TaskSerializer, many=True, required=True,
                                                description="tasks - note you don't to pass experiment id"),
                               OpenApiParameter(name='samples', type=SampleSerializer, many=True, required=True,
                                                description="samples - note you don't to pass experiment id"),
                               OpenApiParameter(name='stimuli', type=StimulusSerializer, many=True, required=True,
                                                description="stimuli - note you don't to pass experiment id"),
                               OpenApiParameter(name='measures', type=MeasureSerializer, many=True, required=True,
                                                description="measures - note you don't to pass experiment id"),
                               OpenApiParameter(name='interpretations', type=InterpretationCreateSerializer, many=True,
                                                required=True,
                                                description="interpretations - note you don't to pass experiment id"),
                               OpenApiParameter(name='consciousness_measures', type=ConsciousnessMeasureSerializer,
                                                many=True,
                                                required=True,
                                                description="consciousness_measures - note you don't to pass experiment id"),
                               OpenApiParameter(name='finding_tags', type=FindingTagSerializer, many=True,
                                                required=True,
                                                description="finding_tags - note you don't to pass experiment id"),
                               OpenApiParameter(name='techniques', type=str, many=True,
                                                required=True,
                                                description="techniques names"),
                               OpenApiParameter(name='paradigms', type=str, many=True,
                                                required=True,
                                                description="paradigms names"),
                               OpenApiParameter(name='theory_driven_theories', type=str, many=True,
                                                required=True,
                                                description="theory_driven_theories names"),
                               OpenApiParameter(name="is_reporting", type=str, description="is reporting",
                                                enum=[option[0] for option in ReportingChoices.choices]),
                               OpenApiParameter(name="theory_driven", type=str, description="theory driven",
                                                enum=[option[0] for option in TheoryDrivenChoices.choices]),
                               OpenApiParameter(name='notes', type=str, many=False,
                                                required=False,
                                                description="notes"),
                               OpenApiParameter(name='finding_description', type=str, many=False,
                                                required=True,
                                                description="finding description"),
                               OpenApiParameter(name='type', type=int, many=False, required=False,
                                                default=ExperimentTypeChoices.NEUROSCIENTIFIC,
                                                enum=[option[0] for option in ExperimentTypeChoices.choices])

                               ])
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
                                   serializer_cls=InterpretationCreateSerializer)

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

    @extend_schema(parameters=[OpenApiParameter(name='tasks', type=TaskSerializer, many=True, required=True,
                                                description="tasks - note you don't to pass experiment id"),
                               OpenApiParameter(name='samples', type=SampleSerializer, many=True, required=True,
                                                description="samples - note you don't to pass experiment id"),
                               OpenApiParameter(name='stimuli', type=StimulusSerializer, many=True, required=True,
                                                description="stimuli - note you don't to pass experiment id"),
                               OpenApiParameter(name='measures', type=MeasureSerializer, many=True, required=True,
                                                description="measures - note you don't to pass experiment id"),
                               OpenApiParameter(name='interpretations', type=InterpretationCreateSerializer, many=True,
                                                required=True,
                                                description="interpretations - note you don't to pass experiment id"),
                               OpenApiParameter(name='consciousness_measures', type=ConsciousnessMeasureSerializer,
                                                many=True,
                                                required=True,
                                                description="consciousness_measures - note you don't to pass experiment id"),
                               OpenApiParameter(name='finding_tags', type=FindingTagSerializer, many=True,
                                                required=True,
                                                description="finding_tags - note you don't to pass experiment id"),
                               OpenApiParameter(name='techniques', type=str, many=True,
                                                required=True,
                                                description="techniques names"),
                               OpenApiParameter(name='paradigms', type=str, many=True,
                                                required=True,
                                                description="paradigms names"),
                               OpenApiParameter(name='theory_driven_theories', type=str, many=True,
                                                required=True,
                                                description="theory_driven_theories names"),
                               OpenApiParameter(name="is_reporting", type=str, description="is reporting",
                                                enum=[option[0] for option in ReportingChoices.choices]),
                               OpenApiParameter(name="theory_driven", type=str, description="theory driven",
                                                enum=[option[0] for option in TheoryDrivenChoices.choices]),
                               OpenApiParameter(name='notes', type=str, many=False,
                                                required=False,
                                                description="notes"),
                               OpenApiParameter(name='finding_description', type=str, many=False,
                                                required=True,
                                                description="finding description"),
                               OpenApiParameter(name='type', type=int, many=False, required=False,
                                                default=ExperimentTypeChoices.NEUROSCIENTIFIC,
                                                enum=[option[0] for option in ExperimentTypeChoices.choices])

                               ])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
