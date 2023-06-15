import copy

from rest_framework import mixins, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.models import Study
from studies.serializers import StudyWithExperimentsSerializer


class SubmitStudiesViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           GenericViewSet):
    """
    Getting/creating studies I've submitted, editing, etc
    Also allows single link of a specific stufy (as result of search perhaps)
    And searching for studies by title/DOI
    """
    queryset = Study.objects.select_related("approval_process") \
        .prefetch_related("experiments",
                          "authors",
                          "experiments__stimuli",
                          "experiments__stimuli__category",
                          "experiments__stimuli__modality",
                          "experiments__stimuli__sub_category",
                          "experiments__samples",
                          "experiments__tasks",
                          "experiments__tasks__type",
                          "experiments__consciousness_measures",
                          "experiments__consciousness_measures__phase",
                          "experiments__consciousness_measures__type",
                          "experiments__finding_tags",
                          "experiments__finding_tags__family",
                          "experiments__finding_tags__type",
                          "experiments__finding_tags__technique"
                          ) \
        .order_by("-id", "approval_status")
    permission_classes = [IsAuthenticated]
    serializer_class = StudyWithExperimentsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', "DOI"]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ['my_studies']:
            # for my studies we need to limit that
            qs = qs.filter(submitter=self.request.user)
        if self.action in ["update", "partial_update"]:
            # we can update only items still in pending status and that are 'mine"
            qs = qs.filter(approval_status=ApprovalChoices.PENDING) \
                .filter(submitter=self.request.user)
        return qs

    @action(detail=False, methods=["GET"])
    def my_studies(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        data["submitter"] = request.user.id
        data["approval_status"] = ApprovalChoices.PENDING
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        authors = serializer.validated_data.get("authors")
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
