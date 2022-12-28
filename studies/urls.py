from django.urls import path, include
from rest_framework.routers import SimpleRouter

from studies.views import ApprovedStudiesViewSet, ExcludedStudiesViewSet, ExperimentsViewSet

router = SimpleRouter()

router.register(r'studies', ApprovedStudiesViewSet, basename="studies")
router.register(r'excluded_studies', ExcludedStudiesViewSet, basename="excluded_studies")
router.register(r'experiments', ExperimentsViewSet, basename="experiments")

urlpatterns = [
    path('', include(router.urls))
]

