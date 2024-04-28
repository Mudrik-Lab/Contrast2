import logging

import pandas
from django.core.management import BaseCommand
from django.db import transaction

from contrast_api.data_migration_functionality.create_study import create_study
from studies.parsers.parsing_findings_Contrast2 import FindingTagDataError
from contrast_api.data_migration_functionality.errors import (
    MissingStimulusCategoryError,
    ParadigmDataException,
    ProblemInTheoryDrivenExistingDataException,
    IncoherentSampleDataError,
    SampleTypeError,
    ProblemInCMExistingDataException,
    IncoherentStimuliData,
    MissingValueInStimuli,
    StimulusDurationError,
)
from contrast_api.data_migration_functionality.helpers import get_list_from_excel
from contrast_api.data_migration_functionality.studies_parsing_helpers import ProblemInStudyExistingDataException
from uncontrast_studies.management.commands.process_uncon_row import process_uncon_row

logger = logging.getLogger("UnConTrast")

FILE_PATH = "uncontrast_studies/data/__Maors_dataset_for_migration.xlsx"


class Command(BaseCommand):
    help = "Load uncon existing data"

    def handle(self, *args, **options):
        # Read .xlsx file and convert to dict
        historic_data_list = get_list_from_excel(FILE_PATH, sheet_name="Experiments")
        studies_historic_data_list = get_list_from_excel(FILE_PATH, sheet_name="Metadata")

        # iterate over studies
        studies_problematic_data_log = []
        for study_item in studies_historic_data_list:
            try:
                with transaction.atomic():
                    create_study(item=study_item, unconsciousness=True)
            except ProblemInStudyExistingDataException:
                studies_problematic_data_log.append(study_item)

        # iterate over experiments
        stimuli_incoherent_data_log = []
        stimuli_duration_data_log = []
        stimuli_missing_value_data_log = []
        stimuli_missing_object_data_log = []
        paradigms_log = []
        sample_incoherent_data_log = []
        sample_type_errors_log = []
        experiment_studies_problematic_data_log = []
        consciousness_measure_problematic_data_log = []

        duplicated_experiments = {}

        for item in historic_data_list:
            index = historic_data_list.index(item)

            try:
                with transaction.atomic():
                    experiment_duplicate = process_uncon_row(item, duplicated_experiments)
                    if experiment_duplicate is not None:
                        duplicated_experiments[experiment_duplicate.key] = experiment_duplicate.id

                    print(f"row #{index} completed")

            except IncoherentStimuliData:
                stimuli_incoherent_data_log.append(item)
                logger.exception(f"row #{index} has incoherent stimuli data")

            except ParadigmDataException:
                paradigms_log.append(item)
                logger.exception(f"row #{index} has bad paradigm data")

            except MissingValueInStimuli:
                stimuli_missing_value_data_log.append(item)
                logger.exception(f"row #{index} is missing 1 or more values in stimuli data")

            except StimulusDurationError:
                stimuli_duration_data_log.append(item)
                logger.exception(f"row #{index} has problematic stimulus duration data")

            except MissingStimulusCategoryError:
                stimuli_missing_object_data_log.append(item)
                logger.exception(f"row #{index} did not find matching stimulus category or sub-category")

            except IncoherentSampleDataError:
                sample_incoherent_data_log.append(item)
                logger.exception(f"row #{index} has incoherent sample data")

            except SampleTypeError:
                sample_type_errors_log.append(item)
                logger.exception(f"row #{index} is problematic regarding to sample type")

            except ProblemInStudyExistingDataException:
                experiment_studies_problematic_data_log.append(item)
                logger.exception(f"row #{index} is problematic regarding to study data")

            except ProblemInCMExistingDataException:
                consciousness_measure_problematic_data_log.append(item)
                logger.exception(f"row #{index} is problematic regarding to consciousness measure data")

            # iterate over problematic data and add them to .xlsx file in respective sheets
            df_studies = pandas.DataFrame.from_records(studies_problematic_data_log)
            df_paradigms = pandas.DataFrame.from_records(paradigms_log)
            df_incoherent_stimuli = pandas.DataFrame.from_records(stimuli_incoherent_data_log)
            df_missing_value_stimuli = pandas.DataFrame.from_records(stimuli_missing_value_data_log)
            df_bad_duration_stimuli = pandas.DataFrame.from_records(stimuli_duration_data_log)
            df_missing_category_stimuli = pandas.DataFrame.from_records(stimuli_missing_object_data_log)
            df_incoherent_sample = pandas.DataFrame.from_records(sample_incoherent_data_log)
            df_sample_type = pandas.DataFrame.from_records(sample_type_errors_log)
            df_study_in_experiment = pandas.DataFrame.from_records(experiment_studies_problematic_data_log)
            df_consciousness_measure = pandas.DataFrame.from_records(consciousness_measure_problematic_data_log)

            try:
                with pandas.ExcelWriter("uncontrast_studies/data/UnContrast_Problematic_Data.xlsx") as writer:
                    df_studies.to_excel(writer, sheet_name="StudyData", index=False)
                    df_paradigms.to_excel(writer, sheet_name="ParadigmData", index=False)
                    df_incoherent_stimuli.to_excel(writer, sheet_name="IncoherentStimuli", index=False)
                    df_missing_value_stimuli.to_excel(writer, sheet_name="MissingValueStimuliData", index=False)
                    df_bad_duration_stimuli.to_excel(writer, sheet_name="StimulusDuration", index=False)
                    df_missing_category_stimuli.to_excel(writer, sheet_name="StimulusCategory", index=False)
                    df_incoherent_sample.to_excel(writer, sheet_name="IncoherentSample", index=False)
                    df_sample_type.to_excel(writer, sheet_name="SampleType", index=False)
                    df_study_in_experiment.to_excel(writer, sheet_name="ExperimentStudyData", index=False)
                    df_consciousness_measure.to_excel(writer, sheet_name="ConsciousnessMeasureData", index=False)
            except AttributeError as error:
                logger.exception(f"{error.name} occurred while writing to excel")
