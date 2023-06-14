from rest_framework import mixins, permissions
from rest_framework.viewsets import GenericViewSet
from rest_framework import filters

from studies.serializers import AuthorSerializer


class AuthorsViewSet(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     GenericViewSet):
    """
    Basically to populate the authors drop down with auto complete + allow to create new ones
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']



