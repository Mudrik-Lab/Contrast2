from collections import namedtuple

from configuration.uncontrast_initial_data_types import uncon_paradigms, uncon_tasks, uncon_processing_domains
from contrast_api.data_migration_functionality.errors import ParadigmError, TaskTypeError, ProcessingDomainError

UnconResolvedParadigmData = namedtuple("UnconParadigmFromData", ["main", "specific"])


def resolve_uncon_paradigm(item, index: str):
    main_paradigm = str(item["Paradigms Main paradigm"]).strip()
    specific_paradigm = str(item["Paradigms Specific paradigm"]).strip()

    if main_paradigm not in uncon_paradigms.keys():
        raise ParadigmError(f"index {index} missing main paradigm: {main_paradigm}.")
    if len(uncon_paradigms[main_paradigm]) == 0:
        specific_paradigm = main_paradigm
    elif specific_paradigm not in uncon_paradigms[main_paradigm]:
        raise ParadigmError(f"index {index} invalid specific paradigm: {specific_paradigm}.")

    return UnconResolvedParadigmData(main=main_paradigm, specific=specific_paradigm)


def resolve_uncon_task_type(item: dict, index: str):
    task_data_list = clean_list_from_data(item["Tasks Type"])
    resolved_task_data_list = []

    for task_data in task_data_list:
        if task_data not in uncon_tasks:
            raise TaskTypeError(f"invalid task: {task_data}, index {index}")
        else:
            resolved_task_data_list.append(task_data)

    return resolved_task_data_list


def resolve_uncon_processing_domains(item: dict, index: str):
    resolved_processing_domains = []
    processing_domain_data = clean_list_from_data(item["Processing domain"])
    for processing_domain_data in processing_domain_data:
        if processing_domain_data in uncon_processing_domains:
            resolved_processing_domains.append(processing_domain_data)
        else:
            raise ProcessingDomainError(f"invalid processing domain {processing_domain_data}, index: {index}")

    return resolved_processing_domains


def clean_list_from_data(data: object, integer: bool = False) -> list:
    list_from_data = str(data).split(";")
    stripped_list_from_data = [int(item) if integer and item.isdigit() else item.strip() for item in list_from_data]

    return stripped_list_from_data
