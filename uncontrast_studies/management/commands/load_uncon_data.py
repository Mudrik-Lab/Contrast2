import logging
from datetime import date

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
    FindingError,
    IncoherentStimuliDataError,
    NumericListError,
    MissingValueInStimuliError,
)
from contrast_api.data_migration_functionality.helpers import get_list_from_excel
from contrast_api.data_migration_functionality.studies_parsing_helpers import (
    ProblemInStudyExistingDataException,
    MissingCountryDetectionException,
)
from uncontrast_studies.services.process_uncon_row import process_uncon_row
from uncontrast_studies.services.uncontrast_logger import write_to_log

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load uncontrast existing data"

    def add_arguments(self, parser):
        parser.add_argument("-f", "--filename", type=str, help="Filename to load")
        parser.add_argument("--dev", action='store_true', help="Start dev data migration process")

    def handle(self, *args, **options):
        if options["dev"]:
            filename = options["filename"]
        else:
            filename = "staging_data"

        file_path = f"uncontrast_studies/data/{filename}.xlsx"
        current_date = date.today()
        error_log_path = f"uncontrast_studies/data/logs/uncontrast_errors_log_{current_date}.xlsx"
        success_log_path = f"uncontrast_studies/data/logs/uncontrast_success_log_{current_date}.xlsx"

        # Read .xlsx file and convert to dict
        experiments_data_list = get_list_from_excel(file_path, sheet_name="experiments")
        studies_historic_data_list = get_list_from_excel(file_path, sheet_name="Metadata")

        errors_logs = {
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
            "stimuli_numeric_data_log": [],
            "invalid_stimuli_metadata_log": [],
            "sample_type_errors_log": [],
            "sample_size_errors_log": [],
            "invalid_numeric_data_log": [],
        }

        success_logs = {"Metadata": [], "experiments": []}

        # iterate over studies
        created_studies = []
        for study_item in studies_historic_data_list:
            study_doi = study_item["DOI"]
            if study_doi in created_studies:
                continue
            else:
                try:
                    with transaction.atomic():
                        create_study(item=study_item, unconsciousness=True)
                        created_studies.append(study_doi)
                        success_logs["Metadata"].append(study_item)

                except ProblemInStudyExistingDataException:
                    errors_logs["studies_problematic_data_log"].append(study_item)

                except MissingCountryDetectionException:
                    errors_logs["studies_problematic_data_log"].append(study_item)

        # iterate over experiments
        for index, item in enumerate(experiments_data_list):
            index = index + 1
            try:
                with transaction.atomic():
                    process_uncon_row(item)
                    print(f"row #{index} completed")
                    success_logs["experiments"].append(item)

            except ParadigmError:
                errors_logs["invalid_paradigm_data_log"].append(item)
                logger.exception(f"row #{index} has invalid paradigm data")

            except TaskTypeError:
                errors_logs["invalid_task_data_log"].append(item)
                logger.exception(f"row #{index} has invalid task data")

            except ProcessingDomainError:
                errors_logs["invalid_processing_domain_data_log"].append(item)
                logger.exception(f"row #{index} has invalid processing domain data")

            except SuppressionMethodError:
                errors_logs["invalid_suppression_method_data_log"].append(item)
                logger.exception(f"row #{index} has invalid suppression method data")

            except IncoherentStimuliDataError:
                errors_logs["incoherent_stimuli_data_log"].append(item)
                logger.exception(f"row #{index} has incoherent stimulus data")

            except StimulusModeOfPresentationError:
                errors_logs["invalid_stimuli_presentation_mode_data_log"].append(item)
                logger.exception(f"row #{index} has invalid stimulus MoP data")

            except StimulusMetadataError:
                errors_logs["invalid_stimuli_metadata_log"].append(item)
                logger.exception(f"row #{index} has invalid stimulus metadata")

            except StimulusDurationError:
                errors_logs["stimuli_numeric_data_log"].append(item)
                logger.exception(f"row #{index} has invalid stimulus numeric data")

            except StimulusModalityError:
                errors_logs["invalid_stimuli_modality_data_log"].append(item)
                logger.exception(f"row #{index} has invalid stimulus modality data")

            except (MissingStimulusCategoryError, MissingValueInStimuliError):
                errors_logs["stimuli_missing_object_data_log"].append(item)
                logger.exception(f"row #{index} did not find matching stimulus category or sub-category")

            except SampleTypeError:
                errors_logs["sample_type_errors_log"].append(item)
                logger.exception(f"row #{index} has invalid sample type data")

            except SampleSizeError:
                errors_logs["sample_size_errors_log"].append(item)
                logger.exception(f"row #{index} has invalid sample size data")

            except FindingError:
                errors_logs["invalid_finding_data_log"].append(item)
                logger.exception(f"row #{index} has invalid finding data")

            except ProblemInStudyExistingDataException:
                errors_logs["invalid_study_metadata_log"].append(item)
                logger.exception(f"row #{index} has invalid study metadata")

            except InvalidConsciousnessMeasureDataError:
                errors_logs["invalid_consciousness_measure_data_log"].append(item)
                logger.exception(f"row #{index} is problematic regarding to consciousness measure data")

            except NumericListError:
                errors_logs["invalid_numeric_data_log"].append(item)

        sum_of_logs = sum(len(log) for log in errors_logs.values())
        if sum_of_logs > 0:
            print(f"completed loading {len(experiments_data_list)} rows of data, with {sum_of_logs} errors")

            # iterate over invalid-data logs and add them to .xlsx file in respective sheets
            write_to_log(errors_logs, error_log_path)

            # create success log
            write_to_log(success_logs, success_log_path)
