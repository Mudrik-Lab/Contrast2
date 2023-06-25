from typing import Dict

from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from contrast_api.application_services.feedback import FeedbackService
from users.serializers import SuggestNewQuerySerializer, ContactUsSerializer, VetAPaperSerializer, \
    SiteFeedbackSerializer, \
    FeedbackResponseSerializer


class FeedbackView(GenericViewSet):
    permission_classes = (permissions.AllowAny,)

    @extend_schema(responses=FeedbackResponseSerializer)
    @action(methods=["POST"], detail=False, serializer_class=ContactUsSerializer)
    def contact_us(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = FeedbackService()
        service.contact_us(serializer.data)
        return Response(data=dict(submitted=True), status=status.HTTP_201_CREATED)

    @extend_schema(responses=FeedbackResponseSerializer)
    @action(methods=["POST"], detail=False, serializer_class=SuggestNewQuerySerializer)
    def suggest_new_query(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = FeedbackService()
        service.suggest_query(serializer.data)
        return Response(data=dict(submitted=True), status=status.HTTP_201_CREATED)

    @extend_schema(responses=FeedbackResponseSerializer)
    @action(methods=["POST"], detail=False, serializer_class=VetAPaperSerializer)
    def vet_a_paper(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = FeedbackService()
        service.vet_a_paper(serializer.data)
        return Response(data=dict(submitted=True), status=status.HTTP_201_CREATED)

    @extend_schema(responses=FeedbackResponseSerializer)
    @action(methods=["POST"], detail=False, serializer_class=SiteFeedbackSerializer)
    def site_feedback(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = FeedbackService()
        service.site_feedback(serializer.data)
        return Response(data=dict(submitted=True), status=status.HTTP_201_CREATED)
