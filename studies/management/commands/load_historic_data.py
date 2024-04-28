import logging

import pandas
from django.core.management import BaseCommand
from django.db import transaction

from studies.parsers.parsing_findings_Contrast2 import FindingTagDataError
from studies.parsers.process_row import (
    process_row,
)
from contrast_api.data_migration_functionality.create_study import create_study
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

logger = logging.getLogger("Contrast2")


class Command(BaseCommand):
    help = "Load historic data"

    def handle(self, *args, **options):
        # Read .xlsx file and convert to dict
        historic_data_list = get_list_from_excel("studies/data/Contrast2_Existing_Data.xlsx", sheet_name="sheet1")
        studies_historic_data_list = get_list_from_excel(
            "studies/data/Contrast2_Existing_Data.xlsx", sheet_name="Included_Metadata"
        )

        # iterate over studies
        studies_problematic_data_log = []
        for study_item in studies_historic_data_list:
            try:
                with transaction.atomic():
                    create_study(item=study_item, unconsciousness=False)
            except ProblemInStudyExistingDataException:
                studies_problematic_data_log.append(study_item)

        # iterate over experiments
        stimuli_incoherent_data_log = []
        stimuli_duration_data_log = []
        stimuli_missing_value_data_log = []
        stimuli_missing_object_data_log = []
        paradigms_log = []
        theory_driven_problematic_data_log = []
        sample_incoherent_data_log = []
        sample_type_errors_log = []
        experiment_studies_problematic_data_log = []
        consciousness_measure_problematic_data_log = []
        finding_tags_problematic_data_log = []
        items_to_exclude = []

        for item in historic_data_list:
            index = historic_data_list.index(item)
            is_included = bool(item["Should be included?"])
            if not is_included:
                items_to_exclude.append(item)
                print(f"row #{index} removed")
                continue

            try:
                with transaction.atomic():
                    process_row(item)
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

            except ProblemInTheoryDrivenExistingDataException:
                theory_driven_problematic_data_log.append(item)
                logger.exception(f"row #{index} is problematic regarding to theory driven data")

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

            except FindingTagDataError:
                finding_tags_problematic_data_log.append(item)
                logger.exception(f"row #{index} is problematic regarding to finding tag data")

            # iterate over problematic data and add them to .xlsx file in respective sheets
            df_studies = pandas.DataFrame.from_records(studies_problematic_data_log)
            df_paradigms = pandas.DataFrame.from_records(paradigms_log)
            df_incoherent_stimuli = pandas.DataFrame.from_records(stimuli_incoherent_data_log)
            df_missing_value_stimuli = pandas.DataFrame.from_records(stimuli_missing_value_data_log)
            df_bad_duration_stimuli = pandas.DataFrame.from_records(stimuli_duration_data_log)
            df_missing_category_stimuli = pandas.DataFrame.from_records(stimuli_missing_object_data_log)
            df_theory_driven = pandas.DataFrame.from_records(theory_driven_problematic_data_log)
            df_incoherent_sample = pandas.DataFrame.from_records(sample_incoherent_data_log)
            df_sample_type = pandas.DataFrame.from_records(sample_type_errors_log)
            df_study_in_experiment = pandas.DataFrame.from_records(experiment_studies_problematic_data_log)
            df_consciousness_measure = pandas.DataFrame.from_records(consciousness_measure_problematic_data_log)
            df_finding_tag = pandas.DataFrame.from_records(finding_tags_problematic_data_log)
            df_items_to_exclude = pandas.DataFrame.from_records(items_to_exclude)

            try:
                with pandas.ExcelWriter("studies/data/Contrast2_Problematic_Data.xlsx") as writer:
                    df_finding_tag.to_excel(writer, sheet_name="FindingTag", index=False)
                    df_studies.to_excel(writer, sheet_name="StudyData", index=False)
                    df_paradigms.to_excel(writer, sheet_name="ParadigmData", index=False)
                    df_incoherent_stimuli.to_excel(writer, sheet_name="IncoherentStimuli", index=False)
                    df_missing_value_stimuli.to_excel(writer, sheet_name="MissingValueStimuliData", index=False)
                    df_bad_duration_stimuli.to_excel(writer, sheet_name="StimulusDuration", index=False)
                    df_missing_category_stimuli.to_excel(writer, sheet_name="StimulusCategory", index=False)
                    df_theory_driven.to_excel(writer, sheet_name="TheoryDriven", index=False)
                    df_incoherent_sample.to_excel(writer, sheet_name="IncoherentSample", index=False)
                    df_sample_type.to_excel(writer, sheet_name="SampleType", index=False)
                    df_study_in_experiment.to_excel(writer, sheet_name="ExperimentStudyData", index=False)
                    df_consciousness_measure.to_excel(writer, sheet_name="ConsciousnessMeasureData", index=False)
                    df_items_to_exclude.to_excel(writer, sheet_name="ExcludedItems", index=False)
            except AttributeError as error:
                logger.exception(f"{error.name} occurred while writing to excel")
