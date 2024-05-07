import logging

from django.core.management import BaseCommand
from django.db import transaction

from contrast_api.data_migration_functionality.create_study import create_study
from contrast_api.data_migration_functionality.errors import (
    MissingStimulusCategoryError,
    SampleTypeError,
    InvalidConsciousnessMeasureDataError,
    StimulusDurationError,
    ParadigmError,
    TaskTypeError,
    ProcessingDomainError,
    StimulusModalityError,
    StimulusModeOfPresentationError,
    StimulusMetadataError,
    SampleSizeError,
    SuppressionMethodError,
    FindingError, IncoherentStimuliDataError,
)
from contrast_api.data_migration_functionality.helpers import get_list_from_excel
from contrast_api.data_migration_functionality.studies_parsing_helpers import ProblemInStudyExistingDataException
from uncontrast_studies.services.process_uncon_row import process_uncon_row
from uncontrast_studies.services.errors_logger import write_errors_to_log

logger = logging.getLogger("UnConTrast")

FILE_PATH = "uncontrast_studies/data/dataset_05052024.xlsx"
ERROR_LOG_PATH = "uncontrast_studies/data/UnContrast_Errors_Log.xlsx"


class Command(BaseCommand):
    help = "Load uncon existing data"

    def handle(self, *args, **options):
        # Read .xlsx file and convert to dict
        experiments_data_list = get_list_from_excel(FILE_PATH, sheet_name="experiments")
        studies_historic_data_list = get_list_from_excel(FILE_PATH, sheet_name="Metadata")

        logs = {
            "studies_problematic_data_log": [],
            "invalid_study_metadata_log": [],
            "invalid_paradigm_data_log": [],
            "invalid_task_data_log": [],
            "invalid_processing_domain_data_log": [],
            "invalid_suppression_method_data_log": [],
            "invalid_finding_data_log": [],
            "invalid_consciousness_measure_data_log": [],
            "stimuli_missing_object_data_log": [],
            "incoherent_stimuli_data_log": [],
            "invalid_stimuli_modality_data_log": [],
            "invalid_stimuli_presentation_mode_data_log": [],
            "stimuli_duration_data_log": [],
            "invalid_stimuli_metadata_log": [],
            "sample_type_errors_log": [],
            "sample_size_errors_log": [],
        }

        # iterate over studies
        created_studies = []
        for study_item in studies_historic_data_list:
            study_id = study_item["StudyID"]
            if study_id in created_studies:
                continue
            else:
                try:
                    with transaction.atomic():
                        create_study(item=study_item, unconsciousness=True)
                        # created_studies.append(study_id)
                except ProblemInStudyExistingDataException:
                    logs["studies_problematic_data_log"].append(study_item)

        # iterate over experiments
        for item in experiments_data_list:
            index = int(item["exp"])
            is_study_in_metadata = item["is study in metadata"]
            if is_study_in_metadata == "0" or is_study_in_metadata == 0:
                continue
            try:
                with transaction.atomic():
                    process_uncon_row(item)
                    print(f"row #{index} completed")

            except ParadigmError:
                logs["invalid_paradigm_data_log"].append(item)
                logger.exception(f"row #{index} has invalid paradigm data")

            except TaskTypeError:
                logs["invalid_task_data_log"].append(item)
                logger.exception(f"row #{index} has invalid task data")

            except ProcessingDomainError:
                logs["invalid_processing_domain_data_log"].append(item)
                logger.exception(f"row #{index} has invalid processing domain data")

            except SuppressionMethodError:
                logs["invalid_suppression_method_data_log"].append(item)
                logger.exception(f"row #{index} has invalid suppression method data")

            except IncoherentStimuliDataError:
                logs["incoherent_stimuli_data_log"].append(item)
                logger.exception(f"row #{index} has incoherent stimulus data")

            except StimulusModeOfPresentationError:
                logs["invalid_stimuli_presentation_mode_data_log"].append(item)
                logger.exception(f"row #{index} has invalid stimulus MoP data")

            except StimulusMetadataError:
                logs["invalid_stimuli_metadata_log"].append(item)
                logger.exception(f"row #{index} has invalid stimulus metadata")

            except StimulusDurationError:
                logs["stimuli_duration_data_log"].append(item)
                logger.exception(f"row #{index} has invalid stimulus duration numeric data")

            except StimulusModalityError:
                logs["invalid_stimuli_modality_data_log"].append(item)
                logger.exception(f"row #{index} has invalid stimulus modality data")

            except MissingStimulusCategoryError:
                logs["stimuli_missing_object_data_log"].append(item)
                logger.exception(f"row #{index} did not find matching stimulus category or sub-category")

            except SampleTypeError:
                logs["sample_type_errors_log"].append(item)
                logger.exception(f"row #{index} has invalid sample type data")

            except SampleSizeError:
                logs["sample_size_errors_log"].append(item)
                logger.exception(f"row #{index} has invalid sample size data")

            except FindingError:
                logs["invalid_finding_data_log"].append(item)
                logger.exception(f"row #{index} has invalid finding data")

            except ProblemInStudyExistingDataException:
                logs["invalid_study_metadata_log"].append(item)
                logger.exception(f"row #{index} has invalid study metadata")

            except InvalidConsciousnessMeasureDataError:
                logs["invalid_consciousness_measure_data_log"].append(item)
                logger.exception(f"row #{index} is problematic regarding to consciousness measure data")

        # iterate over invalid-data logs and add them to .xlsx file in respective sheets
        write_errors_to_log(logs, ERROR_LOG_PATH)
