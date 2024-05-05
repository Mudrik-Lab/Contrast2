from collections import namedtuple

from configuration.uncontrast_initial_data_types import uncon_suppression_methods
from contrast_api.data_migration_functionality.errors import SuppressionMethodError


def resolve_uncon_suppression_method(item: dict, index: str):
    suppression_methods_list = []
    main_methods = []
    specific_methods = []
    main_suppression_methods_data = str(item["Suppression method Main suppression method"]).split(";")
    specific_suppression_methods_data = str(item["Suppression method Specific suppression method"]).split(";")

    for main_method in main_suppression_methods_data:
        if main_method.strip() in uncon_suppression_methods.keys():
            resolved_main_method = main_method.strip()
            main_methods.append(resolved_main_method)
        else:
            raise SuppressionMethodError(f"invalid main suppression method {main_method}, index {index}")

    for specific_method in specific_suppression_methods_data:
        is_match = False
        for main_method in main_methods:
            if specific_method.strip() in uncon_suppression_methods[main_method]:
                resolved_specific_method = specific_method.strip()
                specific_methods.append(resolved_specific_method)
                is_match = True
            else:
                continue
        if not is_match:
            raise SuppressionMethodError(f"invalid specific suppression method {specific_method}, index {index}")

    if len(main_methods) == 0:
        raise SuppressionMethodError(f"missing main suppression method, index {index}")

    for resolved_main_method in main_methods:
        if len(uncon_suppression_methods[resolved_main_method]) == 0 or len(specific_methods) == 0:
            suppression_method = UnconResolvedSuppressionMethodData(main=resolved_main_method, specific=None)
            suppression_methods_list.append(suppression_method)
        else:
            for resolved_specific_method in specific_methods:
                if resolved_specific_method in uncon_suppression_methods[resolved_main_method]:
                    suppression_method = UnconResolvedSuppressionMethodData(
                        main=resolved_main_method, specific=resolved_specific_method
                    )
                    suppression_methods_list.append(suppression_method)
                else:
                    raise SuppressionMethodError(
                        f"specific suppression method {resolved_specific_method} is invalid "
                        f"for main suppression method: {resolved_main_method}, index {index}"
                    )

    return suppression_methods_list


UnconResolvedSuppressionMethodData = namedtuple("UnconResolvedSuppressionMethodData", ["main", "specific"])
