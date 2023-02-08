from django.core.management import BaseCommand
import pandas
from configuration.initial_setup import techniques, paradigms, finding_tags_map, findings_measures
from studies.choices import ExperimentTypeChoices, InterpretationsChoices, ReportingChoices, TypeOfConsciousnessChoices
from studies.parsers.finding_tag_parsers import parse_findings_per_experiment, FrequencyFinding, TemporalFinding, \
    SpatialFinding
from studies.parsers.historic_data_helpers import get_paradigms_from_data, parse_theory_driven_from_data, \
    parse_task_types, get_measures_from_data, parse_consciousness_measure_type_from_data, \
    parse_consciousness_measure_phases_from_data

from studies.models import Study, Author, Experiment, Technique, FindingTag, FindingTagFamily, Sample, FindingTagType, \
    TaskType, Task, ConsciousnessMeasureType, ConsciousnessMeasurePhaseType, Interpretation, Theory, \
    ConsciousnessMeasure, MeasureType, Measure
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

            study = Study.objects.get_or_create(DOI=item["DOI"], title=item["Title"], year=item["Year"],
                                                corresponding_author_email="placeholder@email", approval_status=1,
                                                authors_key_words=author_keywords, funding=item["Funding.Details"],
                                                source_title=item["Source.Title"],
                                                abbreviated_source_title=item["Abbreviated.Source.Title"],
                                                countries=countries, affiliations=item["Affiliations"])
            # parse authors and add to study
            authors = []
            authors_names = parse_authors_from_authors_text(item["Authors"])
            for author_name in authors_names:
                author = Author.objects.get_or_create(name=author_name)
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

                    experiment_interpretation = Interpretation.objects.get_or_create(experiment=experiment,
                                                                                     theory=theory, type=interpretation)
                    interpretations.append(experiment_interpretation)

            for interpretation in interpretations:
                experiment.interpretations.add(interpretation)

            techniques_in_historic_data = []
            for technique in techniques:
                if technique not in item["Techniques"]:
                    continue
                parsed_technique = Technique.objects.get_or_create(name=technique)
                techniques_in_historic_data.append(parsed_technique)

            for technique in techniques_in_historic_data:
                experiment.techniques.add(technique)

            paradigms_in_data = get_paradigms_from_data(paradigms, item)
            for paradigm in paradigms_in_data:
                experiment.paradigms.add(paradigm)

            # resolve and create findings
            for key in item.keys:
                if 'Findings.NCC Tags' in key:
                    findings_ncc_tags = key
            findings = parse_findings_per_experiment(findings_ncc_tags)

            finding_classes = []
            for finding in findings:
                tag_type = finding_tags_map[finding.tag]
                comment = finding.comment
                if len(techniques_in_historic_data) == 1:
                    technique = techniques_in_historic_data[0]
                else:
                    technique = finding.technique

                if isinstance(finding, FrequencyFinding):
                    finding_class = FindingTag(experiment=experiment, family='Frequency', type=tag_type,
                                               onset=finding.onset, offset=finding.offset,
                                               band_lower_bound=finding.band_low, band_higher_bound=finding.band_high,
                                               notes=comment, analysis_type=finding.analysis,
                                               correlation_sign=finding.cor_type, technique=technique)
                    finding_classes.append(finding_class)
                elif isinstance(finding, TemporalFinding):
                    finding_class = FindingTag(experiment=experiment, family='Temporal', type=tag_type,
                                               onset=finding.onset, offset=finding.offset, notes=comment,
                                               technique=technique)
                    finding_classes.append(finding_class)
                elif isinstance(finding, SpatialFinding):
                    finding_class = FindingTag(experiment=experiment, family='Spatial Areas', type=tag_type,
                                               AAL_atlas_tag=finding.area, notes=comment, technique=technique)
                    finding_classes.append(finding_class)
                else:
                    finding_class = FindingTag(experiment=experiment, family='miscellaneous (no Family)', type=tag_type,
                                               notes=comment)
                    finding_classes.append(finding_class)

            for finding_class in finding_classes:
                FindingTag.objects.create(finding_class)

            # resolve and create consciousness measures
            type_text = item['Measures of consciousness.Measures Taken']
            consciousness_types = parse_consciousness_measure_type_from_data(type_text)
            types = []
            for consciousness_type in consciousness_types:
                consciousness_measure_type = ConsciousnessMeasureType.objects.get_or_create(name=consciousness_type)
                types.append(consciousness_measure_type)

            phase_text = item['Measures of consciousness.Type']
            consciousness_measure_phases = parse_consciousness_measure_phases_from_data(phase_text)
            phases = []
            for consciousness_phase in consciousness_measure_phases:
                consciousness_measure_phase = ConsciousnessMeasurePhaseType.objects.get_or_create(
                    name=consciousness_phase)
                phases.append(consciousness_measure_phase)

            consciousness_measure_description = item["Measures of consciousness.Description"]

            for index in types, phases:
                consciousness_measure_phase = phases[index]
                consciousness_measure_type = types[index]
                ConsciousnessMeasure.objects.get_or_create(experiment=experiment, phase=consciousness_measure_phase,
                                                           type=consciousness_measure_type,
                                                           description=consciousness_measure_description)

            # resolve and create finding measures
            measures = get_measures_from_data(item)
            for measure in measures:
                measure_type = measure.measure_type
                notes = measure.measure_notes
                measure_name = MeasureType.objects.get_or_create(name=measure_type)
                Measure.objects.create(experiment=experiment, type=measure_name, notes=notes)

            # resolve and create samples
            sample_type = item["Sample.Type"]

            Sample.objects.create(experiment=experiment, sample=sample_type, total_size=0,
                                  size_included=["Sample.Included"])  # TODO: write sample size parser

            # resolve and create tasks
            for parsed_task_type in parse_task_types(item):
                task_type = TaskType.objects.get_or_create(name=parsed_task_type)
                description = item["Task.Description"]
                Task.objects.create(experiment=experiment, description=description, type=task_type)

            # stimuli
            modality_type = get_modality_type_from_data(item)
            stimulus_category
            stimulus_description = item["Stimuli Features.Description"]
