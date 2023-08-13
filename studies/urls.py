from django.urls import path, include
from rest_framework_nested import routers

from studies.views import ApprovedStudiesViewSet, ExcludedStudiesViewSet, ExperimentsGraphsViewSet, \
    SubmitStudiesViewSet, SubmittedStudyExperiments
from studies.views.authors import AuthorsViewSet
from studies.views.submitted_studies_experiments_related_objects import StudyExperimentsTasks, StudyExperimentsSamples, \
    StudyExperimentsStimuli, StudyExperimentsMeasures, StudyExperimentsInterpretations, StudyExperimentsFindingTags

router = routers.SimpleRouter()

router.register(r'studies', ApprovedStudiesViewSet, basename="studies")
router.register(r'excluded_studies', ExcludedStudiesViewSet, basename="excluded_studies")
router.register(r'experiments_graphs', ExperimentsGraphsViewSet, basename="experiments-graphs")
router.register(r'authors', AuthorsViewSet, basename="authors")

studies_router = routers.SimpleRouter()
studies_router.register('submitted_studies', SubmitStudiesViewSet, basename="studies-submitted")

studies_experiments_router = routers.NestedSimpleRouter(studies_router, r'submitted_studies', lookup='study')
studies_experiments_router.register("experiments", SubmittedStudyExperiments, basename="studies-experiments")

studies_experiments_nested_router = routers.NestedSimpleRouter(studies_experiments_router, r'experiments',
                                                               lookup='experiment')
studies_experiments_nested_router.register("tasks", StudyExperimentsTasks, basename="tasks")
studies_experiments_nested_router.register("samples", StudyExperimentsSamples, basename="samples")
studies_experiments_nested_router.register("stimuli", StudyExperimentsStimuli, basename="stimuli")
studies_experiments_nested_router.register("measures", StudyExperimentsMeasures, basename="measures")
studies_experiments_nested_router.register("interpretations", StudyExperimentsInterpretations,
                                           basename="interpretations")
studies_experiments_nested_router.register("finding_tags", StudyExperimentsFindingTags, basename="finding_tags")
studies_experiments_nested_router.register("consciousness_measures", StudyExperimentsAnalysisMeasures,
                                           basename="consciousness_measures")


urlpatterns = [
    path('', include(router.urls)),
    path('', include(studies_router.urls)),
    path('', include(studies_experiments_router.urls)),
    path('', include(studies_experiments_nested_router.urls))
]
