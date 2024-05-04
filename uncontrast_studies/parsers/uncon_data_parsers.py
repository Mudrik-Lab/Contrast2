from collections import namedtuple

from configuration.uncontrast_initial_data_types import uncon_paradigms, uncon_tasks, uncon_processing_domains
from contrast_api.data_migration_functionality.errors import ParadigmError, TaskTypeError, \
    ProcessingDomainError

UnconResolvedParadigmData = namedtuple("UnconParadigmFromData", ["main", "specific"])


def resolve_uncon_paradigm(item, index: str):
    main_paradigm = str(item["Paradigms Main paradigm"]).strip()
    specific_paradigm = str(item["Paradigms Specific paradigm"]).strip()

    if main_paradigm not in uncon_paradigms.keys():
        raise ParadigmError(f"index {index} missing main paradigm: {main_paradigm}.")
    if specific_paradigm not in uncon_paradigms[main_paradigm]:
        raise ParadigmError(f"index {index} missing specific paradigm: {specific_paradigm}.")

    return UnconResolvedParadigmData(main=main_paradigm, specific=specific_paradigm)


def resolve_uncon_task(item: dict, index: str):
    task_data = str(item["Tasks Type"]).strip()
    resolved_task_data_list = []

    if ";" in task_data:
        task_data_list = task_data.split(";")
        for task_data in task_data_list:
            task_data = task_data.strip()
            if task_data not in uncon_tasks:
                raise TaskTypeError(f"task error for {index}: {task_data}")
            else:
                resolved_task_data_list.append(task_data)
    else:
        if task_data not in uncon_tasks:
            raise TaskTypeError(f"task error for {index}: {task_data}")
        else:
            resolved_task_data_list.append(task_data)

    return resolved_task_data_list


def resolve_uncon_processing_domains(item: dict, index: str):
    resolved_processing_domains = []
    processing_domain_data = str(item["Processing domain"]).split(";")
    for processing_domain_data in processing_domain_data:
        main_domain_data = processing_domain_data.strip()
        if main_domain_data in uncon_processing_domains:
            resolved_processing_domains.append(main_domain_data)
        else:
            raise ProcessingDomainError(f"invalid processing domain {main_domain_data}, index: {index}")

    return resolved_processing_domains
