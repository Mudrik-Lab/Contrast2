from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from contrast_api.application_services.feedback import FeedbackService
from users.serializers import (
    SuggestNewQuerySerializer,
    ContactUsSerializer,
    VetAPaperSerializer,
    SiteFeedbackSerializer,
    FeedbackResponseSerializer,
)





class FeedbackView(GenericViewSet):
    permission_classes = (permissions.AllowAny,)

    def resolve_site_from_request(self, request):
        if self.basename == "feedback_uncontrast":
            return "UnContrast"
        else:
            return "Contrast"

    @extend_schema(responses=FeedbackResponseSerializer)
    @action(methods=["POST"], detail=False, serializer_class=ContactUsSerializer)
    def contact_us(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        site_name = self.resolve_site_from_request(request)
        service = FeedbackService(site_name)
        service.contact_us(serializer.data)
        return Response(data=dict(submitted=True), status=status.HTTP_201_CREATED)

    @extend_schema(responses=FeedbackResponseSerializer)
    @action(methods=["POST"], detail=False, serializer_class=SuggestNewQuerySerializer)
    def suggest_new_query(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        site_name = self.resolve_site_from_request(request)
        service = FeedbackService(site_name)
        service.suggest_query(serializer.data)
        return Response(data=dict(submitted=True), status=status.HTTP_201_CREATED)

    @extend_schema(responses=FeedbackResponseSerializer)
    @action(methods=["POST"], detail=False, serializer_class=VetAPaperSerializer)
    def vet_a_paper(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        site_name = self.resolve_site_from_request(request)
        service = FeedbackService(site_name)
        service.vet_a_paper(serializer.data)
        return Response(data=dict(submitted=True), status=status.HTTP_201_CREATED)

    @extend_schema(responses=FeedbackResponseSerializer)
    @action(methods=["POST"], detail=False, serializer_class=SiteFeedbackSerializer)
    def site_feedback(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        site_name = self.resolve_site_from_request(request)
        service = FeedbackService(site_name)
        service.site_feedback(serializer.data)
        return Response(data=dict(submitted=True), status=status.HTTP_201_CREATED)
