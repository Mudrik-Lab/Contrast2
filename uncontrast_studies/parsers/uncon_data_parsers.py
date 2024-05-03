from collections import namedtuple

from configuration.uncontrast_initial_data_types import uncon_paradigms, uncon_tasks, uncon_processing_domains
from contrast_api.data_migration_functionality.errors import ParadigmError, TaskTypeError, \
    ProcessingDomainError

UnconResolvedParadigmData = namedtuple("UnconParadigmFromData", ["main", "specific"])


def resolve_uncon_paradigm(item):
    main_paradigm = str(item["Paradigms Main paradigm"]).strip()
    specific_paradigm = str(item["Paradigms Specific paradigm"]).strip()

    if main_paradigm not in uncon_paradigms.keys():
        raise ParadigmError(f"missing main paradigm: {main_paradigm}.")
    if specific_paradigm not in uncon_paradigms.values():
        raise ParadigmError(f"missing specific paradigm: {specific_paradigm}.")

    return UnconResolvedParadigmData(main=main_paradigm, specific=specific_paradigm)


def resolve_uncon_task(item: dict, index: str):
    task_data = str(item["Tasks Type"]).strip()

    if task_data not in uncon_tasks:
        raise TaskTypeError(f"task error for {index}: {task_data}")

    return task_data


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
