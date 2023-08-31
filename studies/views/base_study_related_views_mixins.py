import copy

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
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

    @extend_schema(parameters=[OpenApiParameter(location="path", name="study_pk", type=str),
                               OpenApiParameter(location="path", name="experiment_pk", type=str)])
    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, self.parent_object)

        return obj


class ExperimentRelatedNestedObjectMixin:
    """
    Mixin to be used with GenericViewSet
    """
    def get_queryset(self):
        qs = super().get_queryset() \
            .filter(experiment_id=self.kwargs.get("experiment_pk"))
        return qs

    @extend_schema(parameters=[OpenApiParameter(location="path", name="study_pk", type=str),
                               OpenApiParameter(location="path", name="experiment_pk", type=str)])
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