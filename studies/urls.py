from django.urls import path, include
from rest_framework_nested import routers

from studies.views import ApprovedStudiesViewSet, ExcludedStudiesViewSet, ExperimentsGraphsViewSet, \
    SubmitStudiesViewSet, SubmittedStudyExperiments

router = routers.SimpleRouter()

router.register(r'studies', ApprovedStudiesViewSet, basename="studies")
router.register(r'excluded_studies', ExcludedStudiesViewSet, basename="excluded_studies")
router.register(r'experiments_graphs', ExperimentsGraphsViewSet, basename="experiments-graphs")

studies_router = routers.SimpleRouter()
studies_router.register('submitted_studies', SubmitStudiesViewSet, basename="studies-submitted")

studies_experiments_router = routers.NestedSimpleRouter(studies_router, r'submitted_studies', lookup='study')
studies_experiments_router.register("experiments", SubmittedStudyExperiments, basename="studies-experiments")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(studies_router.urls)),
    path('', include(studies_experiments_router.urls))
]

