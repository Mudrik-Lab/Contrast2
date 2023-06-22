from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from users.serializers import SuggestNewQuerySerializer, ContactUsSerializer, VetAPaperSerializer, FeedbackSerializer


class FeedbackView(GenericViewSet):

    @action(methods=["POST"], detail=False, serializer_class=ContactUsSerializer)
    def contact_us(self, request, *args, **kwargs):
        return Response(data=dict(submitted=True), status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, serializer_class=SuggestNewQuerySerializer)
    def suggest_new_query(self, request, *args, **kwargs):
        return Response(data=dict(submitted=True), status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, serializer_class=VetAPaperSerializer)
    def vet_a_paper(self, request, *args, **kwargs):
        return Response(data=dict(submitted=True), status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, serializer_class=FeedbackSerializer)
    def feedback(self, request, *args, **kwargs):
        return Response(data=dict(submitted=True), status=status.HTTP_200_OK)


