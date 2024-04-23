from django_countries import countries
from import_export import resources
from import_export.fields import Field

from contrast_api.choices import ExperimentTypeChoices, SignificanceChoices
from uncontrast_studies.models import UnConExperiment

SEPERATOR = " || "


class FullUnConExperimentResource(resources.ModelResource):
    Experiment_id = Field(attribute="id")
    DOI = Field(attribute="study__DOI")
    Journal = Field(attribute="study__source_title")
    Title = Field(attribute="study__title")
    Authors = Field(dehydrate_method="dehydrate_authors")
    Is_the_author_the_submitter = Field(attribute="study__is_author_submitter")
    Year = Field(attribute="study__year")
    Countries_of_affiliation = Field(dehydrate_method="dehydrate_countries")
    Type_of_experiment = Field(dehydrate_method="dehydrate_type")
    Experiment_paradigm = Field(dehydrate_method="dehydrate_paradigms")
    Samples = Field(dehydrate_method="dehydrate_samples")
    Consciousness_measures = Field(dehydrate_method="dehydrate_consciousness_measures")
    Suppressed_stimuli = Field(dehydrate_method="dehydrate_suppressed_stimuli")
    Target_stimuli = Field(dehydrate_method="dehydrate_target_stimuli")
    Tasks = Field(dehydrate_method="dehydrate_tasks")
    findings = Field(dehydrate_method="dehydrate_finding")
    Consciousness_measures_notes = Field(attribute="consciousness_measures_notes")
    Is_target_same_as_suppressed_stimulus = Field(attribute="is_target_same_as_suppressed_stimulus")
    Is_target_stimulus = Field(attribute="is_target_stimulus")
    Significance = Field(attribute="dehydrate_significance")
    Experiment_findings_notes = Field(attribute="experiment_findings_notes")
    Processing_domains = Field(dehydrate_method="dehydrate_processing_domains")
    Suppression_methods = Field(dehydrate_method="dehydrate_suppression_methods")

    class Meta:
        model = UnConExperiment
        fields = (
            "DOI",
            "Title",
            "Authors",
            "Is_the_author_the_submitter",
            "Year",
            "Journal",
            "Countries_of_affiliation",
            "Experiment_id",
            "Type_of_experiment",
            "Experiment_paradigm",
            "Samples",
            "Tasks",
            "Suppressed_stimuli",
            "Target_stimuli",
            "Consciousness_measures",
            "Is_target_same_as_suppressed_stimulus",
            "Is_target_stimulus",
            "findings",
            "Experiment_findings_notes",
            "Processing_domains",
            "Suppression_methods",
            "Significance"
        )

        export_order = fields

    def dehydrate_countries(self, experiment: UnConExperiment):
        return SEPERATOR.join(countries.name(country) for country in experiment.study.countries)

    def dehydrate_authors(self, experiment: UnConExperiment):
        return SEPERATOR.join(author.name for author in experiment.study.authors.all())

    def dehydrate_interpretations(self, experiment: UnConExperiment):
        return SEPERATOR.join(
            [
                f"{interpretation.parent_theory_acronyms} - {interpretation.type}"
                for interpretation in experiment.aggregated_theories.all()
            ]
        )

    def dehydrate_paradigms(self, experiment: UnConExperiment):
        return experiment.paradigm.name

    def dehydrate_samples(self, experiment: UnConExperiment):
        return SEPERATOR.join(
            f"{sample.type} -excluded: {sample.size_excluded} -included: {sample.size_included}"
            for sample in experiment.samples.all()
        )

    def dehydrate_consciousness_measures(self, experiment: UnConExperiment):
        return SEPERATOR.join(
            f"{cm.type.name} - phase: {cm.phase.name}" for cm in experiment.unconsciousness_measures.all()
        )

    def dehydrate_suppressed_stimuli(self, experiment: UnConExperiment):
        return SEPERATOR.join(
            f"category: {st.category.name} {'(' + st.sub_category.name + ')' if st.sub_category else ''} -modality: {st.modality.name} "
            for st in experiment.suppressed_stimuli.all()
        )

    def dehydrate_target_stimuli(self, experiment: UnConExperiment):
        return SEPERATOR.join(
            f"category: {st.category.name} {'(' + st.sub_category.name + ')' if st.sub_category else ''} -modality: {st.modality.name} "
            for st in experiment.target_stimuli.all()
        )

    def dehydrate_tasks(self, experiment: UnConExperiment):
        return SEPERATOR.join(task.type.name for task in experiment.uncon_tasks.all())

    def dehydrate_processing_domains(self, experiment: UnConExperiment):
        return SEPERATOR.join(f"{domain.main} {domain.sub_domain}" for domain in experiment.processing_domains.all())

    def dehydrate_suppression_methods(self, experiment: UnConExperiment):
        return SEPERATOR.join(
            f"{method.type.name} - {method.sub_type.name if method.sub_type is not None else None}"
            for method in experiment.suppression_methods.all()
        )

    def dehydrate_finding(self, experiment: UnConExperiment):
        return SEPERATOR.join(self.resolve_finding_tag_description(finding) for finding in experiment.findings.all())

    def resolve_finding_tag_description(self, finding):
        return f"outcome: {finding.outcome} is_significant: {finding.is_significant}"

    def dehydrate_type(self, experiment: UnConExperiment):
        return next(label for value, label in ExperimentTypeChoices.choices if value == experiment.type)

    def dehydrate_significance(self, experiment: UnConExperiment):
        return next(label for value, label in SignificanceChoices.choices if value == experiment.significance)

