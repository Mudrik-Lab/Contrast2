from import_export import resources
from import_export.fields import Field

from studies.choices import ExperimentTypeChoices
from studies.models import Experiment, Study


class FullExperimentResource(resources.ModelResource):
    authors = Field()
    interpretations = Field()
    techniques = Field()
    paradigms = Field()
    measures = Field()
    samples = Field()
    consciousness_measures = Field()
    stimuli = Field()
    tasks = Field()
    finding_tags = Field()
    theory_driven_theories = Field()
    type = Field()

    class Meta:
        model = Experiment
        fields = (
            "study__DOI",
            "study__title",
            "authors",
            "study__corresponding_author_email",
            "study__year",
            "study__funding",
            "study__source_title",
            "study__countries",
            "study__affiliations",
            "id",
            "results_summary",
            "techniques",
            "interpretations",
            "paradigms",
            "type_of_consciousness",
            "is_reporting",
            "theory_driven",
            "theory_driven_theories",
            "type",
            "consciousness_measures",
            "finding_tags",
            "measures",
            "samples",
            "stimuli",
            "tasks",
            "tasks_notes",
            "consciousness_measures_notes",
            "stimuli_notes",
            "paradigms_notes",
            "sample_notes",
        )

        export_order = fields

    def dehydrate_authors(self, experiment: Experiment):
        return "|".join(author.name for author in experiment.study.authors.all())

    def dehydrate_techniques(self, experiment: Experiment):
        return "|".join(technique.name for technique in experiment.techniques.all())

    def dehydrate_interpretations(self, experiment: Experiment):
        return "|".join(
            [
                f"{interpretation.parent_theory_names} - {interpretation.type}"
                for interpretation in experiment.aggregated_theories.all()
            ]
        )

    def dehydrate_paradigms(self, experiment: Experiment):
        return "|".join(paradigm.name for paradigm in experiment.paradigms.all())

    def dehydrate_measures(self, experiment: Experiment):
        return "|".join(measure.type.name for measure in experiment.measures.all())

    def dehydrate_samples(self, experiment: Experiment):
        return "|".join(
            f"{sample.type} - {sample.total_size} - {sample.size_included}" for sample in experiment.samples.all()
        )

    def dehydrate_consciousness_measures(self, experiment: Experiment):
        return "|".join(f"{cm.type.name} - {cm.phase.name}" for cm in experiment.consciousness_measures.all())

    def dehydrate_stimuli(self, experiment: Experiment):
        return "|".join(
            f"{st.category.name} {'(' + st.sub_category.name + ')' if st.sub_category else ''} - {st.modality.name} "
            for st in experiment.stimuli.all()
        )

    def dehydrate_tasks(self, experiment: Experiment):
        return "|".join(task.type.name for task in experiment.tasks.all())

    def dehydrate_finding_tags(self, experiment: Experiment):
        return "|".join(finding.type.name for finding in experiment.finding_tags.all())

    def dehydrate_theory_driven_theories(self, experiment: Experiment):
        return "|".join([theory.name for theory in experiment.theory_driven_theories.all()])

    def dehydrate_type(self, experiment: Experiment):
        return next(label for value, label in ExperimentTypeChoices.choices if value == experiment.type)
