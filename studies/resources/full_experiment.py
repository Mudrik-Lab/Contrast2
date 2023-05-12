from django.db.models import Prefetch
from import_export import resources
from import_export.fields import Field

from studies.models import Experiment, Paradigm


class FullExperimentResource(resources.ModelResource):
    authors = Field()

    class Meta:
        model = Experiment
        fields = ('study__title',
                  'authors',
                  'study__year',
                  'study__funding',
                  'study__source_title',
                  'study__countries',
                  'study__affiliations',
                  'id',
                  'finding_description',
                  'techniques',
                  'interpretations',
                  'paradigms',
                  'type_of_consciousness',
                  'is_reporting',
                  'theory_driven',
                  'theory_driven_theories',
                  'type',
                  'consciousness_measures',
                  'finding_tags',
                  'measures',
                  'samples',
                  'stimuli',
                  'tasks',
                  'notes')

    def get_queryset(self):
        return super().get_queryset().select_related("study")\
            .prefetch_related(Prefetch('paradigms', queryset=Paradigm.objects.select_related('parent'))) \
            .prefetch_related("study__authors")


    def dehydrate_authors(self, experiment):
        return "|".join(author.name for author in experiment.study.authors.all())
