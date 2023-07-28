import copy

from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.models import Study, Measure, FindingTag, Task, ConsciousnessMeasure, Stimulus, Paradigm
from studies.permissions import SubmitterOnlyPermission
from studies.serializers import StudyWithExperimentsSerializer, ThinStudyWithExperimentsSerializer, \
    StudyWithExperimentsCreateSerializer


class SubmitStudiesViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           GenericViewSet):
    """
    Getting/creating studies I've submitted, editing, etc
    Also allows single link of a specific study (as result of search perhaps)
    And searching for studies by title/DOI
    """
    queryset = Study.objects.select_related("approval_process") \
        .prefetch_related("experiments",
                          "authors",
                          "experiments__techniques",
                          "experiments__theory_driven_theories",
                          "experiments__aggregated_theories",
                          Prefetch('experiments__measures', queryset=Measure.objects.select_related("type")),
                          Prefetch('experiments__tasks', queryset=Task.objects.select_related("type")),
                          Prefetch('experiments__finding_tags', queryset=FindingTag.objects.select_related("type")),
                          Prefetch('experiments__consciousness_measures',
                                   queryset=ConsciousnessMeasure.objects.select_related("type", "phase")),
                          Prefetch('experiments__stimuli',
                                   queryset=Stimulus.objects.select_related("category", "sub_category",
                                                                            "modality")),
                          Prefetch('experiments__paradigms',
                                   queryset=Paradigm.objects.select_related('parent', 'parent__parent')),
                          "experiments__samples",

                          ) \
        .order_by("-id", "approval_status")
    permission_classes = [SubmitterOnlyPermission]
    serializer_class = StudyWithExperimentsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', "DOI"]

    def get_serializer_class(self):
        if self.action in ['list', 'my_studies']:
            return ThinStudyWithExperimentsSerializer
        if self.action in ["create", "update", "partial_update"]:
            return StudyWithExperimentsCreateSerializer
        else:
            return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ['my_studies']:
            # for my studies we need to limit that
            qs = qs.filter(submitter=self.request.user)
        if self.action in ["update", "partial_update", "delete"]:
            # we can update only items still in pending status and that are 'mine"
            qs = qs.filter(approval_status=ApprovalChoices.PENDING) \
                .filter(submitter=self.request.user)
        return qs

    @extend_schema(responses=ThinStudyWithExperimentsSerializer)
    def list(self, request, *args, **kwargs):
        """
        This should be used only to search for a submitted study with the search filter.. and not generally
        Note this endpoint is paginated and returns a "thin" experiment
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["GET"])
    def my_studies(self, request, *args, **kwargs):
        """
        The right endpoint to use when working with "my" submissions.
        Currently this is unpaginated, as paginating this is tricky from the UI perspective
        """
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=StudyWithExperimentsCreateSerializer, responses=StudyWithExperimentsSerializer)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        result_serializer = StudyWithExperimentsSerializer(instance=updated_instance)

        return Response(result_serializer.data)

    @extend_schema(request=StudyWithExperimentsCreateSerializer, responses=StudyWithExperimentsSerializer)
    def create(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        data["submitter"] = request.user.id
        data["approval_status"] = ApprovalChoices.PENDING
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)

        result_serializer = StudyWithExperimentsSerializer(instance=instance)

        return Response(result_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
