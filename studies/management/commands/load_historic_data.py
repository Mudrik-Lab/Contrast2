import logging

import numpy
import pandas

from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Model

from configuration.initial_setup import techniques, paradigms, finding_tags_map, parent_theories
from studies.choices import ExperimentTypeChoices, InterpretationsChoices, ReportingChoices, TypeOfConsciousnessChoices
from studies.models.stimulus import StimulusCategory, StimulusSubCategory, Stimulus
from studies.parsers.finding_tag_parsers import parse_findings_per_experiment, FrequencyFinding, TemporalFinding, \
    SpatialFinding, FindingTagDataError
from studies.parsers.historic_data_helpers import get_paradigms_from_data, parse_theory_driven_from_data, \
    parse_task_types, get_measures_from_data, get_stimuli_from_data, get_consciousness_measure_type_and_phase_from_data, \
    get_sample_from_data, ProblemInTheoryDrivenExistingDataException, \
    ProblemInSampleExistingDataException, ProblemInCMExistingDataException, IncoherentStimuliData, \
    MissingValueInStimuli, StimulusDurationError

from studies.models import Study, Author, Experiment, Technique, FindingTag, FindingTagFamily, Sample, FindingTagType, \
    TaskType, Task, ConsciousnessMeasureType, ConsciousnessMeasurePhaseType, Theory, \
    ConsciousnessMeasure, MeasureType, Measure, ModalityType, Paradigm
from studies.parsers.parsing_findings_Contrast2 import parse
from studies.parsers.studies_parsing_helpers import parse_authors_from_authors_text, parse_authors_keywords_from_text, \
    resolve_country_from_affiliation_text, validate_year, ProblemInStudyExistingDataException

logger = logging.getLogger('Contrast2')


class MissingStimulusCategoryError(Exception):
    pass


class Command(BaseCommand):
    help = 'Load historic data'

    def create_experiment(self, item: dict):
        # start with straight-forward data (study, finding description, type)
        try:
            study = Study.objects.get(DOI=item["Paper.DOI"])
        except ObjectDoesNotExist:
            raise ProblemInStudyExistingDataException()

        finding_description = item["Findings.Summary"]
        experiment_type = ExperimentTypeChoices.NEUROSCIENTIFIC

        # resolve choices fields (theory_driven, type_of_consciousness, is_reporting)
        theories = parent_theories
        theory_driven, theory_driven_theories = parse_theory_driven_from_data(item, theories)

        type_of_consciousness = ""
        type_of_consciousness_choice = item['State - Content']
        if type_of_consciousness_choice == "0":
            type_of_consciousness = TypeOfConsciousnessChoices.STATE
        elif type_of_consciousness_choice == "1":
            type_of_consciousness = TypeOfConsciousnessChoices.CONTENT
        elif type_of_consciousness_choice == "2":
            type_of_consciousness = TypeOfConsciousnessChoices.BOTH

        is_reporting = ""
        reporting_choice = item['Experimental paradigms.Report']
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
        logger.info(f'experiment {experiment.id} for study {study.DOI} created')

        return experiment, theory_driven_theories

    def create_study(self, item: dict):
        # parse author keywords and countries from text
        text = item["Author.Keywords"]
        author_keywords = parse_authors_keywords_from_text(text)
        countries = list(resolve_country_from_affiliation_text(item["Affiliations"]))
        year = validate_year(item["Year"])
        funding = str(item["Funding.Details"])

        study, created = Study.objects.get_or_create(DOI=item["DOI"], title=item["Title"], year=year,
                                                     corresponding_author_email="placeholder@email",
                                                     approval_status=1, authors_key_words=author_keywords,
                                                     funding=funding, source_title=item["Source.Title"],
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

        logger.info(f'study {study.DOI} created')
        return study

    def convert_to_df(self, data_list: list):
        if len(data_list):
            data_frame = pandas.DataFrame.from_records(data_list)
            return data_frame
        pass

    def process_row(self, item: dict):
        experiment, theory_driven_theories = self.create_experiment(item)

        # resolve and add ManyToMany fields (theory-driven theories, interpretations, paradigms, techniques)
        for theory in theory_driven_theories:
            theory = Theory.objects.get(name=theory)
            experiment.theory_driven_theories.add(theory)

        theories = parent_theories
        interpretation = ""
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
            interpretation_theory = Theory.objects.get(name=theory)
            experiment.interpretations.add(interpretation_theory,
                                           through_defaults={'type': interpretation})

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
            paradigm = Paradigm.objects.get(name=name, parent=parent)
            experiment.paradigms.add(paradigm)

        # resolve and create consciousness measures
        consciousness_measures_from_data = get_consciousness_measure_type_and_phase_from_data(item)
        try:
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
        except ObjectDoesNotExist:
            raise ProblemInCMExistingDataException()

        # resolve and create finding measures
        measures = get_measures_from_data(item)
        for measure in measures:
            measure_type = measure.measure_type
            notes = measure.measure_notes
            measure_name = MeasureType.objects.get(name=measure_type)
            Measure.objects.create(experiment=experiment, type=measure_name, notes=notes)

        # resolve and create samples
        try:
            sample_from_data = get_sample_from_data(item)
            sample_type = sample_from_data.sample_type
            total_size = int(sample_from_data.total_size)
            included_size = int(sample_from_data.included_size)
            note = sample_from_data.note
            Sample.objects.create(experiment=experiment, type=sample_type, total_size=total_size,
                                  size_included=included_size)
            if note is not None:
                experiment.notes = note
                experiment.save()

        except ValueError as error:
            logger.exception(f'{error} while processing sample data')
            raise ProblemInSampleExistingDataException

        # resolve and create tasks
        for parsed_task_type in parse_task_types(item):
            task_type = TaskType.objects.get(name=parsed_task_type)
            description = item["Task.Description"]
            Task.objects.create(experiment=experiment, description=description, type=task_type)

        # resolve and create stimuli
        stimuli_from_data = get_stimuli_from_data(item)
        stimulus_sub_category = ""
        for stimulus in stimuli_from_data:
            if (stimulus.duration is None) or (stimulus.duration == 'None'):
                duration = None
            else:
                duration = float(stimulus.duration)
            stimulus_description = item["Stimuli Features.Description"]
            try:
                modality_type = ""
                if stimulus.modality:
                    modality_type = ModalityType.objects.get(name=stimulus.modality)
                stimulus_category = StimulusCategory.objects.get(name=stimulus.category)
                if (stimulus.sub_category == "") or (stimulus.sub_category is None):
                    stimulus_sub_category = None
                else:
                    stimulus_sub_category = StimulusSubCategory.objects.get(
                        name=stimulus.sub_category, parent=stimulus.category)
                Stimulus.objects.create(experiment=experiment, category=stimulus_category,
                                        sub_category=stimulus_sub_category,
                                        modality=modality_type, description=stimulus_description,
                                        duration=duration)

            except ObjectDoesNotExist or ValueError as error:
                logger.exception(f'{error} while processing stimuli data')
                raise MissingStimulusCategoryError()

        # resolve and create findings
        findings_ncc_tags = item["Findings.NCC Tags"]
        try:
            # findings = parse_findings_per_experiment(findings_ncc_tags)
            findings = parse(findings_ncc_tags)
            for finding in findings:
                resolved_tag_type = finding_tags_map[finding.tag]
                comment = finding.comment
                if len(techniques_in_historic_data) == 1:
                    technique = techniques_in_historic_data[0]
                else:
                    technique = finding.technique

                if isinstance(finding, FrequencyFinding):
                    family_name = 'Frequency'
                    family = FindingTagFamily.objects.get(name=family_name)
                    tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                    FindingTag.objects.create(experiment=experiment, family=family, type=tag_type,
                                              onset=finding.onset, offset=finding.offset,
                                              band_lower_bound=finding.band_low,
                                              band_higher_bound=finding.band_high,
                                              notes=comment, analysis_type=finding.analysis,
                                              correlation_sign=finding.cor_type, technique=technique)

                elif isinstance(finding, TemporalFinding):
                    family_name = 'Temporal'
                    family = FindingTagFamily.objects.get(name=family_name)
                    tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                    FindingTag.objects.create(experiment=experiment, family=family, type=tag_type,
                                              onset=finding.onset, offset=finding.offset, notes=comment,
                                              technique=technique)

                elif isinstance(finding, SpatialFinding):
                    family_name = 'Spatial Areas'
                    family = FindingTagFamily.objects.get(name=family_name)
                    tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                    FindingTag.objects.create(experiment=experiment, family=family, type=tag_type,
                                              AAL_atlas_tag=finding.area, notes=comment,
                                              technique=technique)

                else:
                    family_name = 'miscellaneous (no Family)'
                    family = FindingTagFamily.objects.get(name=family_name)
                    tag_type = FindingTagType.objects.get(name=resolved_tag_type, family=family)
                    FindingTag.objects.create(experiment=experiment, family=family, type=tag_type,
                                              notes=comment)
        except (ValueError, IndexError, KeyError, FindingTagType.DoesNotExist, IntegrityError) as error:
            logger.exception(f'{error} while processing finding tag data')
            raise FindingTagDataError()

    def handle(self, *args, **options):

        # Read Excel document and convert to dict
        experiments_data_df = pandas.read_excel('studies/data/Contrast2_Data_For_Drorsoft.xlsx', sheet_name='sheet1')
        problematic_finding_tag_data_df = pandas.read_excel('studies/data/Contrast2_Data_For_Drorsoft.xlsx',
                                                            sheet_name='FindingTagData')
        studies_data_df = pandas.read_excel('studies/data/Contrast2_Data_For_Drorsoft.xlsx',
                                            sheet_name='Included_Metadata')
        no_nan_studies_data_df = studies_data_df.replace(numpy.nan, "")
        no_nan_experiments_data_df = experiments_data_df.replace(numpy.nan, "")
        no_nan_finding_tag_data_df = problematic_finding_tag_data_df.replace(numpy.nan, "")
        studies_historic_data_list = no_nan_studies_data_df.to_dict("records")
        historic_data_list = no_nan_experiments_data_df.to_dict("records")
        finding_tag_data_list = no_nan_finding_tag_data_df.to_dict("records")
        full_data_list = historic_data_list + finding_tag_data_list

        # iterate over studies
        studies_problematic_data_log = []
        for study_item in studies_historic_data_list:
            try:
                with transaction.atomic():
                    self.create_study(item=study_item)
            except ProblemInStudyExistingDataException:
                studies_problematic_data_log.append(study_item)

        # iterate over experiments
        stimuli_incoherent_data_log = []
        stimuli_duration_data_log = []
        stimuli_missing_value_data_log = []
        stimuli_missing_object_data_log = []
        theory_driven_problematic_data_log = []
        sample_problematic_data_log = []
        experiment_studies_problematic_data_log = []
        consciousness_measure_problematic_data_log = []
        finding_tags_problematic_data_log = []
        items_to_exclude = []

        for item in finding_tag_data_list:
            index = finding_tag_data_list.index(item)
            is_included = bool(item["Should be included?"])
            if not is_included:
                items_to_exclude.append(item)
                # historic_data_list.remove(item)
                logger.info(f'row #{index} removed')
                continue

            try:
                with transaction.atomic():
                    self.process_row(item)
                    logger.info(f'row #{index} completed')

            except IncoherentStimuliData:
                stimuli_incoherent_data_log.append(item)
                logger.exception(f'row #{index} has incoherent stimuli data')

            except MissingValueInStimuli:
                stimuli_missing_value_data_log.append(item)
                logger.exception(f'row #{index} is missing 1 or more values in stimuli data')

            except StimulusDurationError:
                stimuli_duration_data_log.append(item)
                logger.exception(f'row #{index} has problematic stimulus duration data')

            except MissingStimulusCategoryError:
                stimuli_missing_object_data_log.append(item)
                logger.exception(f'row #{index} did not find matching stimulus category or sub-category')

            except ProblemInTheoryDrivenExistingDataException:
                theory_driven_problematic_data_log.append(item)
                logger.exception(f'row #{index} is problematic regarding to theory driven data')

            except ProblemInSampleExistingDataException:
                sample_problematic_data_log.append(item)
                logger.exception(f'row #{index} is problematic regarding to sample data')

            except ProblemInStudyExistingDataException:
                experiment_studies_problematic_data_log.append(item)
                logger.exception(f'row #{index} is problematic regarding to study data')

            except ProblemInCMExistingDataException:
                consciousness_measure_problematic_data_log.append(item)
                logger.exception(f'row #{index} is problematic regarding to consciousness measure data')

            except FindingTagDataError:
                finding_tags_problematic_data_log.append(item)
                logger.exception(f'row #{index} is problematic regarding to finding tag data')

            # iterate over problematic data and add them to .xlsx file in respective sheets
            df_studies = pandas.DataFrame.from_records(studies_problematic_data_log)
            df_incoherent_stimuli = pandas.DataFrame.from_records(stimuli_incoherent_data_log)
            df_missing_value_stimuli = pandas.DataFrame.from_records(stimuli_missing_value_data_log)
            df_bad_duration_stimuli = pandas.DataFrame.from_records(stimuli_duration_data_log)
            df_missing_category_stimuli = pandas.DataFrame.from_records(stimuli_missing_object_data_log)
            df_theory_driven = pandas.DataFrame.from_records(theory_driven_problematic_data_log)
            df_sample = pandas.DataFrame.from_records(sample_problematic_data_log)
            df_study_in_experiment = pandas.DataFrame.from_records(experiment_studies_problematic_data_log)
            df_consciousness_measure = pandas.DataFrame.from_records(consciousness_measure_problematic_data_log)
            df_finding_tag = pandas.DataFrame.from_records(finding_tags_problematic_data_log)
            df_items_to_exclude = pandas.DataFrame.from_records(items_to_exclude)

            try:
                with pandas.ExcelWriter('studies/data/Contrast2_Problematic_Data.xlsx') as writer:
                    df_finding_tag.to_excel(writer, sheet_name='FindingTagData', index=False)
                    df_studies.to_excel(writer, sheet_name='StudyData', index=False)
                    df_incoherent_stimuli.to_excel(writer, sheet_name='IncoherentStimuliData', index=False)
                    df_missing_value_stimuli.to_excel(writer, sheet_name='MissingValueStimuliData', index=False)
                    df_bad_duration_stimuli.to_excel(writer, sheet_name='StimulusDurationData', index=False)
                    df_missing_category_stimuli.to_excel(writer, sheet_name='StimulusCategoryData', index=False)
                    df_theory_driven.to_excel(writer, sheet_name='TheoryDrivenData', index=False)
                    df_sample.to_excel(writer, sheet_name='SampleData', index=False)
                    df_study_in_experiment.to_excel(writer, sheet_name='ExperimentStudyData', index=False)
                    df_consciousness_measure.to_excel(writer, sheet_name='ConsciousnessMeasureData', index=False)
                    df_items_to_exclude.to_excel(writer, sheet_name='ExcludedItems', index=False)
            except AttributeError as error:
                logger.exception(f'{error.name} occurred while writing to excel')
