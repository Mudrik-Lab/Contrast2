from django_countries import countries
from import_export import resources
from import_export.fields import Field

from studies.choices import ExperimentTypeChoices
from studies.models import Experiment, Study

SEPERATOR = " || "


class FullExperimentResource(resources.ModelResource):
    Experiment_id = Field(attribute="id")
    DOI = Field(attribute="study__DOI")
    Journal = Field(attribute="study__source_title")
    Title = Field(attribute="study__title")
    Authors = Field(dehydrate_method="dehydrate_authors")
    Is_the_author_the_submitter = Field(attribute="study__is_author_submitter")
    Year = Field(attribute="study__year")
    Countries_of_affiliation = Field(dehydrate_method="dehydrate_countries")
    Type_of_experiment = Field(dehydrate_method="dehydrate_type")
    NCC_results_summary = Field(attribute="results_summary")
    Support_or_Challenges_interpretations = Field(dehydrate_method="dehydrate_interpretations")
    Type_of_consciousness = Field(attribute="type_of_consciousness")
    Techniques = Field(dehydrate_method="dehydrate_techniques")
    Experiment_paradigm = Field(dehydrate_method="dehydrate_paradigms")
    Measures = Field(dehydrate_method="dehydrate_measures")
    Samples = Field(dehydrate_method="dehydrate_samples")
    Consciousness_measures = Field(dehydrate_method="dehydrate_consciousness_measures")
    Stimuli = Field(dehydrate_method="dehydrate_stimuli")
    Tasks = Field(dehydrate_method="dehydrate_tasks")
    NCC_findings = Field(dehydrate_method="dehydrate_finding_tags")
    Driven_by_theories = Field(attribute="theory_driven_theories")
    Is_the_experiment_theory_driven = Field(attribute="theory_driven")
    Sample_notes = Field(attribute="sample_notes")
    Tasks_notes = Field(attribute="tasks_notes")
    Stimuli_notes = Field(attribute="stimuli_notes")
    Paradigms_notes = Field(attribute="paradigms_notes")
    Consciousness_measures_notes = Field(attribute="consciousness_measures_notes")

    class Meta:
        model = Experiment
        fields = (
            "DOI",
            "Title",
            "Authors",
            "Is_the_author_the_submitter",
            "Year",
            "Journal",
            "Countries_of_affiliation",
            "Experiment_id",
            "NCC_results_summary",
            "Type_of_experiment",
            "Is_the_experiment_theory_driven",
            "Driven_by_theories",
            "Support_or_Challenges_interpretations",
            "Type_of_consciousness",
            "is_reporting",
            "Experiment_paradigm",
            "Paradigms_notes",
            "Samples",
            "Sample_notes",
            "Tasks",
            "Tasks_notes",
            "Stimuli",
            "Stimuli_notes",
            "Consciousness_measures",
            "Consciousness_measures_notes",
            "Techniques",
            "Measures",
            "NCC_findings",
        )

        export_order = fields

    def dehydrate_countries(self, experiment: Experiment):
        return SEPERATOR.join(countries.name(country) for country in experiment.study.countries)

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
        return SEPERATOR.join(
            self.resolve_finding_tag_description(finding) for finding in experiment.finding_tags.all())

    def resolve_finding_tag_description(self, finding):
        return f"type: {finding.type.name} family: {finding.family.name} is_NCC: {finding.is_NCC}"

    def dehydrate_theory_driven_theories(self, experiment: Experiment):
        return SEPERATOR.join([theory.name for theory in experiment.theory_driven_theories.all()])

    def dehydrate_type(self, experiment: Experiment):
        return next(label for value, label in ExperimentTypeChoices.choices if value == experiment.type)
