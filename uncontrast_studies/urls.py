from django.urls import path, include
from rest_framework_nested import routers


from studies.views.authors import AuthorsViewSet
from uncontrast_studies.views import SubmitUnContrastStudiesViewSet

router = routers.SimpleRouter()

router.register(r"authors", AuthorsViewSet, basename="authors")

studies_router = routers.SimpleRouter()
studies_router.register("submitted_studies", SubmitUnContrastStudiesViewSet, basename="studies-submitted")

# studies_experiments_router = routers.NestedSimpleRouter(studies_router, r"submitted_studies", lookup="study")
# studies_experiments_router.register("experiments", SubmittedStudyExperiments, basename="studies-experiments")

# studies_experiments_nested_router = routers.NestedSimpleRouter(
#     studies_experiments_router, r"experiments", lookup="experiment"
# )
# studies_experiments_nested_router.register("tasks", StudyExperimentsTasks, basename="tasks")
# studies_experiments_nested_router.register("samples", StudyExperimentsSamples, basename="samples")
# studies_experiments_nested_router.register("stimuli", StudyExperimentsStimuli, basename="stimuli")
#
# studies_experiments_nested_router.register("finding_tags", StudyExperimentsFindingTags, basename="finding_tags")
# studies_experiments_nested_router.register(
#     "consciousness_measures", StudyExperimentsConsciousnessMeasures, basename="consciousness_measures"
# )


urlpatterns = [
    path("", include(router.urls)),
    path("", include(studies_router.urls)),
]
