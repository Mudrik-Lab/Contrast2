from django.urls import path, include
from rest_framework_nested import routers


from studies.views.authors import AuthorsViewSet
from uncontrast_studies.views import SubmitUnContrastStudiesViewSet
from uncontrast_studies.views.experiments_graphs import UnConExperimentsGraphsViewSet
from uncontrast_studies.views.submitted_studies_experiments import SubmittedUnContrastStudyExperiments
from uncontrast_studies.views.submitted_studies_experiments_related_objects import (
    StudyExperimentsTasks,
    StudyExperimentsSamples,
    StudyExperimentsSuppressedStimuli,
    StudyExperimentsTargetStimuli,
    StudyExperimentsFinding,
    StudyExperimentsConsciousnessMeasures,
    StudyExperimentsUnConProcessingDomain,
    StudyExperimentsUnConSuppressionMethod,
)

router = routers.SimpleRouter()

router.register(r"authors", AuthorsViewSet, basename="authors")
router.register(r"experiments_graphs", UnConExperimentsGraphsViewSet, basename="uncontrast-experiments-graphs")

studies_router = routers.SimpleRouter()
studies_router.register("submitted_studies", SubmitUnContrastStudiesViewSet, basename="uncontrast-studies-submitted")

studies_experiments_router = routers.NestedSimpleRouter(studies_router, r"submitted_studies", lookup="study")
studies_experiments_router.register(
    "experiments", SubmittedUnContrastStudyExperiments, basename="uncontrast-studies-experiments"
)

studies_experiments_nested_router = routers.NestedSimpleRouter(
    studies_experiments_router, r"experiments", lookup="experiment"
)
studies_experiments_nested_router.register("tasks", StudyExperimentsTasks, basename="uncontrast-tasks")
studies_experiments_nested_router.register("samples", StudyExperimentsSamples, basename="uncontrast-samples")
studies_experiments_nested_router.register(
    "suppressed_stimuli", StudyExperimentsSuppressedStimuli, basename="uncontrast-suppressed-stimuli"
)
studies_experiments_nested_router.register(
    "target_stimuli", StudyExperimentsTargetStimuli, basename="uncontrast-target-stimuli"
)
#
studies_experiments_nested_router.register("findings", StudyExperimentsFinding, basename="uncontrast-findings")
studies_experiments_nested_router.register(
    "processing_domains", StudyExperimentsUnConProcessingDomain, basename="uncontrast-processing_domains"
)
studies_experiments_nested_router.register(
    "suppression_methods", StudyExperimentsUnConSuppressionMethod, basename="uncontrast-suppression_methods"
)
studies_experiments_nested_router.register(
    "consciousness_measures", StudyExperimentsConsciousnessMeasures, basename="uncontrast-consciousness_measures"
)


urlpatterns = [
    path("", include(router.urls)),
    path("", include(studies_router.urls)),
    path("", include(studies_experiments_router.urls)),
    path("", include(studies_experiments_nested_router.urls)),
]
