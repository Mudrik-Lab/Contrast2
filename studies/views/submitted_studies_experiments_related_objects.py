from rest_framework.viewsets import ModelViewSet, GenericViewSet

from studies.models import Task, Sample, Stimulus, Measure, Interpretation, FindingTag, ConsciousnessMeasure
from studies.permissions import SubmitterOnlyPermission
from studies.serializers import TaskSerializer, SampleSerializer, StimulusSerializer, MeasureSerializer, \
    InterpretationCreateSerializer, FindingTagSerializer, ConsciousnessMeasureSerializer
from studies.views.base_study_related_views_mixins import StudyRelatedPermissionsViewMixin, \
    ExperimentRelatedNestedObjectMixin


class StudyExperimentsTasks(ModelViewSet,
                            GenericViewSet,
                            StudyRelatedPermissionsViewMixin,
                            ExperimentRelatedNestedObjectMixin):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsSamples(ModelViewSet,
                              GenericViewSet,
                              StudyRelatedPermissionsViewMixin,
                              ExperimentRelatedNestedObjectMixin):
    serializer_class = SampleSerializer
    queryset = Sample.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsStimuli(ModelViewSet,
                              GenericViewSet,
                              StudyRelatedPermissionsViewMixin,
                              ExperimentRelatedNestedObjectMixin):
    serializer_class = StimulusSerializer
    queryset = Stimulus.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsMeasures(ModelViewSet,
                               GenericViewSet,
                               StudyRelatedPermissionsViewMixin,
                               ExperimentRelatedNestedObjectMixin):
    serializer_class = MeasureSerializer
    queryset = Measure.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsInterpretations(ModelViewSet,
                                      GenericViewSet,
                                      StudyRelatedPermissionsViewMixin,
                                      ExperimentRelatedNestedObjectMixin):
    serializer_class = InterpretationCreateSerializer
    queryset = Interpretation.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsFindingTags(ModelViewSet,
                                  GenericViewSet,
                                  StudyRelatedPermissionsViewMixin,
                                  ExperimentRelatedNestedObjectMixin):
    serializer_class = FindingTagSerializer
    queryset = FindingTag.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsConsciousnessMeasures(ModelViewSet,
                                            GenericViewSet,
                                            StudyRelatedPermissionsViewMixin,
                                            ExperimentRelatedNestedObjectMixin):
    serializer_class = ConsciousnessMeasureSerializer
    queryset = ConsciousnessMeasure.objects.all()

    permission_classes = [SubmitterOnlyPermission]
