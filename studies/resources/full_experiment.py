from django.db.models import Prefetch
from import_export import resources
from import_export.fields import Field
from django.db import connection

from studies.models import Experiment, Paradigm, Author, Theory, Interpretation


class FullExperimentResource(resources.ModelResource):
    authors = Field()
    interpretations = Field()

    class Meta:
        model = Experiment
        fields = ('study__title',
                  'authors',  # 500 queries
                  'study__year',
                  'study__funding',
                  'study__source_title',
                  'study__countries',
                  'study__affiliations',
                  'id',
                  'finding_description',
                  'techniques',
                  'interpretations',  # 500 queries
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


    def dehydrate_authors(self, experiment):
        return "|".join(author.name for author in experiment.study.authors.all())

    def dehydrate_interpretations(self, experiment):
        interpretations = Interpretation.objects.filter(experiment__id=experiment.id).select_related(
            "experiment",
            "theory__parent",
            'theory__parent__parent')
        return "|".join([f"{interpretation.theory.name} - {interpretation.type}" for interpretation in interpretations])


"""
0385 = {dict: 2} {'sql': 'SELECT "studies_theory"."id", "studies_theory"."name", "studies_theory"."parent_id" FROM "studies_theory" INNER JOIN "studies_experiment_theory_driven_theories" ON ("studies_theory"."id" = "studies_experiment_theory_driven_theories"."theory_id") WHERE "studies_experiment_theory_driven_theories"."experiment_id" = 125', 'time': '0.002'}
0386 = {dict: 2} {'sql': 'SELECT "studies_author"."id", "studies_author"."name" FROM "studies_author" INNER JOIN "studies_study_authors" ON ("studies_author"."id" = "studies_study_authors"."author_id") WHERE "studies_study_authors"."study_id" = 116', 'time': '0.002'}
0387 = {dict: 2} {'sql': 'SELECT "studies_interpretation"."id", "studies_interpretation"."experiment_id", "studies_interpretation"."theory_id", "studies_interpretation"."type", "studies_theory"."id", "studies_theory"."name", "studies_theory"."parent_id", T4."id", T4."name", T4."parent_id", T5."id", T5."name", T5."parent_id" FROM "studies_interpretation" INNER JOIN "studies_theory" ON ("studies_interpretation"."theory_id" = "studies_theory"."id") LEFT OUTER JOIN "studies_theory" T4 ON ("studies_theory"."parent_id" = T4."id") LEFT OUTER JOIN "studies_theory" T5 ON (T4."parent_id" = T5."id") WHERE "studies_interpretation"."experiment_id" = 126', 'time': '0.002'}
"""
