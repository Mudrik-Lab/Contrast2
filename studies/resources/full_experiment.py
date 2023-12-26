from import_export import resources
from import_export.fields import Field

from studies.choices import ExperimentTypeChoices
from studies.models import Experiment, Study

SEPERATOR = " || "


class FullExperimentResource(resources.ModelResource):
    experiment_id = Field(attribute="id")
    journal = Field(attribute="study__source_title")
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
            "study__is_author_submitter",
            "study__year",
            "journal",
            "study__countries",
            "experiment_id",
            "results_summary",
            "type",
            "theory_driven",
            "theory_driven_theories",
            "interpretations",
            "type_of_consciousness",
            "is_reporting",
            "paradigms",
            "paradigms_notes",
            "samples",
            "sample_notes",
            "tasks",
            "tasks_notes",
            "stimuli",
            "stimuli_notes",
            "consciousness_measures",
            "consciousness_measures_notes",
            "techniques",
            "measures",
            "finding_tags",
        )

        export_order = fields

    def dehydrate_authors(self, experiment: Experiment):
        return SEPERATOR.join(author.name for author in experiment.study.authors.all())

    def dehydrate_techniques(self, experiment: Experiment):
        return SEPERATOR.join(technique.name for technique in experiment.techniques.all())

    def dehydrate_interpretations(self, experiment: Experiment):
        return SEPERATOR.join(
            [
                f"{interpretation.parent_theory_acronyms} - {interpretation.type}"
                for interpretation in experiment.aggregated_theories.all()
            ]
        )

    def dehydrate_paradigms(self, experiment: Experiment):
        return SEPERATOR.join(paradigm.name for paradigm in experiment.paradigms.all())

    def dehydrate_measures(self, experiment: Experiment):
        return SEPERATOR.join(measure.type.name for measure in experiment.measures.all())

    def dehydrate_samples(self, experiment: Experiment):
        return SEPERATOR.join(
            f"{sample.type} -total: {sample.total_size} -included: {sample.size_included}" for sample in
            experiment.samples.all()
        )

    def dehydrate_consciousness_measures(self, experiment: Experiment):
        return SEPERATOR.join(
            f"{cm.type.name} - phase: {cm.phase.name}" for cm in experiment.consciousness_measures.all())

    def dehydrate_stimuli(self, experiment: Experiment):
        return SEPERATOR.join(
            f"category: {st.category.name} {'(' + st.sub_category.name + ')' if st.sub_category else ''} -modality: {st.modality.name} "
            for st in experiment.stimuli.all()
        )

    def dehydrate_tasks(self, experiment: Experiment):
        return SEPERATOR.join(task.type.name for task in experiment.tasks.all())

    def dehydrate_finding_tags(self, experiment: Experiment):
        return SEPERATOR.join(self.resolve_finding_tag_description(finding) for finding in experiment.finding_tags.all())

    def resolve_finding_tag_description(self, finding):
        return f"type: {finding.type.name} family: {finding.family.name} is_NCC: {finding.is_NCC}"

    def dehydrate_theory_driven_theories(self, experiment: Experiment):
        return SEPERATOR.join([theory.name for theory in experiment.theory_driven_theories.all()])

    def dehydrate_type(self, experiment: Experiment):
        return next(label for value, label in ExperimentTypeChoices.choices if value == experiment.type)
