from rest_framework.viewsets import ModelViewSet, GenericViewSet

from studies.models import Task, Sample, Stimulus, Measure, Interpretation, FindingTag, ConsciousnessMeasure
from studies.permissions import SubmitterOnlyPermission
from studies.serializers import TaskSerializer, SampleSerializer, StimulusSerializer, MeasureSerializer, \
    InterpretationCreateSerializer, FindingTagSerializer, ConsciousnessMeasureSerializer
from studies.views.base_study_related_views_mixins import StudyRelatedPermissionsViewMixin, \
    ExperimentRelatedNestedObjectMixin


class StudyExperimentsTasks(StudyRelatedPermissionsViewMixin,
                            ExperimentRelatedNestedObjectMixin,
                            ModelViewSet,
                            GenericViewSet,
                            ):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsSamples(StudyRelatedPermissionsViewMixin,
                              ExperimentRelatedNestedObjectMixin,
                              ModelViewSet,
                              GenericViewSet,
                              ):
    serializer_class = SampleSerializer
    queryset = Sample.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsStimuli(StudyRelatedPermissionsViewMixin,
                              ExperimentRelatedNestedObjectMixin,
                              ModelViewSet,
                              GenericViewSet,
                              ):
    serializer_class = StimulusSerializer
    queryset = Stimulus.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsMeasures(StudyRelatedPermissionsViewMixin,
                               ExperimentRelatedNestedObjectMixin,
                               ModelViewSet,
                               GenericViewSet,
                               ):
    serializer_class = MeasureSerializer
    queryset = Measure.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsInterpretations(StudyRelatedPermissionsViewMixin,
                                      ExperimentRelatedNestedObjectMixin,
                                      ModelViewSet,
                                      GenericViewSet,
                                      ):
    serializer_class = InterpretationCreateSerializer
    queryset = Interpretation.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsFindingTags(StudyRelatedPermissionsViewMixin,
                                  ExperimentRelatedNestedObjectMixin,
                                  ModelViewSet,
                                  GenericViewSet,
                                  ):
    serializer_class = FindingTagSerializer
    queryset = FindingTag.objects.all()

    permission_classes = [SubmitterOnlyPermission]


class StudyExperimentsConsciousnessMeasures(StudyRelatedPermissionsViewMixin,
                                            ExperimentRelatedNestedObjectMixin,
                                            ModelViewSet,
                                            GenericViewSet,
                                            ):
    serializer_class = ConsciousnessMeasureSerializer
    queryset = ConsciousnessMeasure.objects.all()

    permission_classes = [SubmitterOnlyPermission]
