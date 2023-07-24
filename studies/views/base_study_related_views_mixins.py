import copy

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from approval_process.choices import ApprovalChoices
from studies.models import Study


class StudyRelatedPermissionsViewMixin:
    def initial(self, request, *args, **kwargs):
        self.parent_object = get_object_or_404(Study.objects.filter(approval_status=ApprovalChoices.PENDING),
                                               id=self.kwargs["study_pk"])
        return super().initial(request, args, kwargs)

    def check_permissions(self, request):
        # we need to verify it has permissions on the parent object, the study
        super().check_permissions(request)
        super().check_object_permissions(request, self.parent_object)


class ExperimentRelatedNestedObjectMixin:
    def get_queryset(self):
        qs = super().get_queryset() \
            .filter(study=self.kwargs.get("experiment_pk"))
        return qs

    def create(self, request, *args, **kwargs):
        """
        Note: DONT pass explicit experiment id in the creation data, as it's provided by the URI
        """
        data = copy.deepcopy(request.data)
        if "experiment" in data.keys():
            data.pop("experiment")
        data["experiment"] = int(self.kwargs.get("experiment_pk"))

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)