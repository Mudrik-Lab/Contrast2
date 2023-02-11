from django.core.management import BaseCommand
import pandas
from configuration.initial_setup import techniques, paradigms, finding_tags_map, findings_measures
from studies.choices import ExperimentTypeChoices, InterpretationsChoices, ReportingChoices, TypeOfConsciousnessChoices
from studies.models.stimulus import StimulusCategory, StimulusSubCategory, Stimulus
from studies.parsers.finding_tag_parsers import parse_findings_per_experiment, FrequencyFinding, TemporalFinding, \
    SpatialFinding
from studies.parsers.historic_data_helpers import get_paradigms_from_data, parse_theory_driven_from_data, \
    parse_task_types, get_measures_from_data, get_stimuli_from_data, get_consciousness_measure_type_and_phase_from_data

from studies.models import Study, Author, Experiment, Technique, FindingTag, FindingTagFamily, Sample, FindingTagType, \
    TaskType, Task, ConsciousnessMeasureType, ConsciousnessMeasurePhaseType, Interpretation, Theory, \
    ConsciousnessMeasure, MeasureType, Measure, ModalityType, Paradigm
from studies.parsers.studies_parsing_helpers import parse_authors_from_authors_text, parse_authors_keywords_from_text, \
    resolve_country_from_affiliation_text


class Command(BaseCommand):
    help = 'Load historic data'

    def handle(self, *args, **options):

        # Read Excel document and convert to dict
        experiments_data_df = pandas.read_excel('studies/data/Contrast2_Data_For_Drorsoft.xlsx', sheet_name='sheet1')
        studies_data_df = pandas.read_excel('studies/data/Contrast2_Data_For_Drorsoft.xlsx',
                                            sheet_name='Included_Metadata')
        studies_historic_data_list = studies_data_df.to_dict("records")
        historic_data_list = experiments_data_df.to_dict("records")

        # iterate over studies
        for item in studies_historic_data_list:
            # parse author keywords and countries from text
            author_keywords = parse_authors_keywords_from_text(item["Author.Keywords"])
            countries = resolve_country_from_affiliation_text(item["Affiliations"])

            study, created = Study.objects.get_or_create(DOI=item["DOI"], title=item["Title"], year=item["Year"],
                                                         corresponding_author_email="placeholder@email",
                                                         approval_status=1,
                                                         authors_key_words=author_keywords,
                                                         funding=item["Funding.Details"],
                                                         source_title=item["Source.Title"],
                                                         abbreviated_source_title=item["Abbreviated.Source.Title"],
                                                         countries=countries, affiliations=item["Affiliations"])
            # parse authors and add to study
            authors = []
            authors_names = parse_authors_from_authors_text(item["Authors"])
            for author_name in authors_names:
                author, created = Author.objects.get_or_create(name=author_name)
                authors.append(author)
            for author in authors:
                study.authors.add(author)

        # iterate over experiments
        for item in historic_data_list:
            is_included = bool(item["Should be included? [0 = Not Included, 1 = Included]"])
            if not is_included:
                historic_data_list.remove(item)

            # start with straight-forward data (study, finding description, type)
            study = Study.objects.get(DOI=item["Paper.DOI"])
            finding_description = item["Findings.Summary"]
            experiment_type = ExperimentTypeChoices.NEUROSCIENTIFIC

            # resolve choices fields (theory_driven, type_of_consciousness, is_reporting)
            theories = ['GNW', 'IIT', 'HOT', 'RPT']
            theory_driven, theory_driven_theories = parse_theory_driven_from_data(item, theories)

            type_of_consciousness_choice = item['State - Content [0=State,1=Content,2 = State And Content]']
            if type_of_consciousness_choice == "0":
                type_of_consciousness = TypeOfConsciousnessChoices.STATE
            elif type_of_consciousness_choice == "1":
                type_of_consciousness = TypeOfConsciousnessChoices.CONTENT
            elif type_of_consciousness_choice == "2":
                type_of_consciousness = TypeOfConsciousnessChoices.BOTH

            reporting_choice = item[
                'Experimental paradigms.Report [0 = No-Report, 1 = Report, 2 = Report And No-Report]']
            if reporting_choice == "0":
                is_reporting = ReportingChoices.NO_REPORT
            elif reporting_choice == "1":
                is_reporting = ReportingChoices.REPORT
            elif reporting_choice == "2":
                is_reporting = ReportingChoices.BOTH

            experiment = Experiment.objects.create(study=study, type_of_consciousness=type_of_consciousness,
                                                   finding_description=finding_description,
                                                   is_reporting=is_reporting, theory_driven=theory_driven,
                                                   type=experiment_type)

            # resolve and add ManyToMany fields (theory-driven theories, interpretations, paradigms, techniques)
            for theory in theory_driven_theories:
                experiment.theory_driven_theories.add(theory)

            interpretations = []
            for theory in theories:
                for key, value in item.items():
                    if theory not in key:
                        continue
                    if value == "1":
                        interpretation = InterpretationsChoices.PRO
                    elif value == "0":
                        interpretation = InterpretationsChoices.CHALLENGES
                    elif value == "X":
                        interpretation = InterpretationsChoices.NEUTRAL

                    experiment_interpretation = Interpretation.objects.create(experiment=experiment,
                                                                              theory=theory, type=interpretation)
                    interpretations.append(experiment_interpretation)

            for interpretation in interpretations:
                experiment.interpretations.add(interpretation)

            techniques_in_historic_data = []
            for technique in techniques:
                if technique not in item["Techniques"]:
                    continue
                parsed_technique = Technique.objects.get(name=technique)
                techniques_in_historic_data.append(parsed_technique)

            for technique in techniques_in_historic_data:
                experiment.techniques.add(technique)

            paradigms_in_data = get_paradigms_from_data(paradigms, item)
            for parsed_paradigm in paradigms_in_data:
                name = parsed_paradigm.name
                parent = parsed_paradigm.parent
                paradigm = Paradigm.objects.create(name=name, parent=parent)
                experiment.paradigms.add(paradigm)

            # resolve and create findings
            findings_ncc_tags = ""
            for key in item.keys():
                if 'Findings.NCC Tags' in key:
                    findings_ncc_tags = key
            findings = parse_findings_per_experiment(findings_ncc_tags)

            for finding in findings:
                resolved_tag_type = finding_tags_map[finding.tag]
                comment = finding.comment
                if len(techniques_in_historic_data) == 1:
                    technique = techniques_in_historic_data[0]
                else:
                    technique = finding.technique

                if isinstance(finding, FrequencyFinding):
                    family = FindingTagFamily.objects.get(name='Frequency')
                    tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                    FindingTag.objects.create(experiment=experiment, family=family, type=tag_type,
                                              onset=finding.onset, offset=finding.offset,
                                              band_lower_bound=finding.band_low,
                                              band_higher_bound=finding.band_high,
                                              notes=comment, analysis_type=finding.analysis,
                                              correlation_sign=finding.cor_type, technique=technique)

                elif isinstance(finding, TemporalFinding):
                    family = FindingTagFamily.objects.get(name='Temporal')
                    tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                    FindingTag.objects.create(experiment=experiment, family=family, type=tag_type,
                                              onset=finding.onset, offset=finding.offset, notes=comment,
                                              technique=technique)

                elif isinstance(finding, SpatialFinding):
                    family = FindingTagFamily.objects.get(name='Spatial Areas')
                    tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                    FindingTag.objects.create(experiment=experiment, family=family, type=tag_type,
                                              AAL_atlas_tag=finding.area, notes=comment,
                                              technique=technique)

                else:
                    family = FindingTagFamily.objects.get(name='miscellaneous (no Family)')
                    tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                    FindingTag.objects.create(experiment=experiment, family=family, type=tag_type,
                                              notes=comment)

            # resolve and create consciousness measures
            consciousness_measures_from_data = get_consciousness_measure_type_and_phase_from_data(item)
            for consciousness_measure in consciousness_measures_from_data:
                consciousness_type = consciousness_measure.type
                consciousness_phase = consciousness_measure.phase
                consciousness_measure_type = ConsciousnessMeasureType.objects.get(name=consciousness_type)
                consciousness_measure_phase = ConsciousnessMeasurePhaseType.objects.get(
                    name=consciousness_phase)
                consciousness_measure_description = item["Measures of consciousness.Description"]
                ConsciousnessMeasure.objects.create(experiment=experiment, phase=consciousness_measure_phase,
                                                    type=consciousness_measure_type,
                                                    description=consciousness_measure_description)
            # resolve and create finding measures
            measures = get_measures_from_data(item)
            for measure in measures:
                measure_type = measure.measure_type
                notes = measure.measure_notes
                measure_name = MeasureType.objects.get(name=measure_type)
                Measure.objects.create(experiment=experiment, type=measure_name, notes=notes)

            # resolve and create samples
            sample_type = item["Sample.Type"]

            Sample.objects.create(experiment=experiment, sample=sample_type, total_size=0,
                                  size_included=["Sample.Included"])  # TODO: write sample size parser

            # resolve and create tasks
            for parsed_task_type in parse_task_types(item):
                task_type = TaskType.objects.get(name=parsed_task_type)
                description = item["Task.Description"]
                Task.objects.create(experiment=experiment, description=description, type=task_type)

            # stimuli
            stimuli_from_data = get_stimuli_from_data(item)
            for stimulus in stimuli_from_data:
                modality_type = ModalityType.objects.get(name=stimulus.modality)
                stimulus_category = StimulusCategory.objects.get(name=stimulus.category)
                if stimulus.sub_category:
                    stimulus_sub_category = StimulusSubCategory.objects.get(
                        name=stimulus.sub_category, parent=stimulus.category)
                duration = int(stimulus.duration)
                stimulus_description = item["Stimuli Features.Description"]
                Stimulus.objects.create(experiment=experiment, category=stimulus_category,
                                        sub_category=stimulus_sub_category,
                                        modality=modality_type, description=stimulus_description, duration=duration)
