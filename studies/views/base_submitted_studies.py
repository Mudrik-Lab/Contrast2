import copy

from django.db.models import Prefetch, Q
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from approval_process.choices import ApprovalChoices
from contrast_api.choices import StudyTypeChoices
from contrast_api.domain_services.study_lifecycle import StudyLifeCycleService
from contrast_api.studies.permissions import SubmitterOnlyPermission
from studies.models import Study
from studies.serializers import (
    ThinStudyWithExperimentsSerializer,
    StudyWithExperimentsCreateSerializer,
    StudyWithExperimentsSerializer,
)


class BaseSubmitStudiesViewSert(ModelViewSet):
    def get_serializer_class(self):
        if self.action in ["list", "my_studies"]:
            return ThinStudyWithExperimentsSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return StudyWithExperimentsCreateSerializer
        else:
            return super().get_serializer_class()

    def get_queryset(self):
        qs = super().get_queryset()
        qs = self.filter_and_prefetch_queryset(qs)
        qs = qs.order_by("-id", "approval_status")
        is_reviewer = (
            hasattr(self, "request") and hasattr(self.request.user, "profile") and self.request.user.profile.is_reviewer
        )
        if self.action in ["my_studies"]:
            # for my studies we need to limit only for studies submitted by the user
            # Unless it's a reviewer user and in this case we add everything pending
            if is_reviewer:
                qs = qs.filter(
                    Q(approval_status__in=[ApprovalChoices.PENDING, ApprovalChoices.AWAITING_REVIEW])
                    | Q(submitter=self.request.user)
                )
            else:
                if not hasattr(self, "request") or self.request.user.is_anonymous():
                    qs = qs.none()
                else:
                    qs = qs.filter(submitter=self.request.user)
        if self.action in ["update", "partial_update", "delete", "submit_to_review"]:
            # we can update only items still in pending status and that are 'mine"

            if is_reviewer:
                # Reviewers can update all items, in both statuses

                qs = qs.filter(approval_status__in=[ApprovalChoices.PENDING, ApprovalChoices.AWAITING_REVIEW])

            else:
                # this extra filter is just for non reviewers
                pending_approval_qs = qs.filter(approval_status=ApprovalChoices.PENDING)
                qs = pending_approval_qs.filter(submitter=self.request.user)

        return qs

    @extend_schema(responses=ThinStudyWithExperimentsSerializer)
    def list(self, request, *args, **kwargs):
        """
        This should be used only to search for a submitted study with the search filter.. and not generally
        Note this endpoint is paginated and returns a "thin" experiment
        """
        return super().list(request, *args, **kwargs)

    @action(methods=["POST"], detail=True, serializer_class=None)
    def submit_to_review(self, request, pk, *args, **kwargs):
        """
        Endpoint to change the study status
        """
        instance: Study = self.get_object()

        service = StudyLifeCycleService()
        service.submitted(instance.submitter, instance)
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["GET"])
    def my_studies(self, request, *args, **kwargs):
        """
        The right endpoint to use when working with "my" submissions.
        Currently, this is unpaginated, as paginating this is tricky from the UI perspective
        """
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=StudyWithExperimentsCreateSerializer, responses=StudyWithExperimentsSerializer)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        if getattr(instance, "_prefetched_objects_cache", None):
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
        data["type"] = self.resolve_study_type(request)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        serializer_class = self.serializer_class
        result_serializer = serializer_class(instance=instance)

        return Response(result_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def resolve_study_type(self, request):
        if self.basename == "uncontrast-studies-submitted":
            return StudyTypeChoices.UNCONSCIOUSNESS
        else:
            return StudyTypeChoices.CONSCIOUSNESS
