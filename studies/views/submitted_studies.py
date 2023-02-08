import copy

from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from approval_process.choices import ApprovalChoices
from studies.models import Study
from studies.serializers import StudyWithExperimentsSerializer


class SubmitStudiesViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           GenericViewSet):
    """
    Getting/creating studies I'm submitting, adding experiments, editing, etc
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
        .filter(approval_status=ApprovalChoices.PENDING)
    permission_classes = [IsAuthenticated]
    serializer_class = StudyWithExperimentsSerializer

    def get_queryset(self):
        return super().get_queryset() \
            .filter(submitter=self.request.user)

    def create(self, request, *args, **kwargs):
        data = copy.deepcopy(request.data)
        data["submitter"] = request.user.id
        data["approval_status"] = ApprovalChoices.PENDING
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
