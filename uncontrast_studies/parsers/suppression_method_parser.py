from collections import namedtuple

from configuration.uncontrast_initial_data_types import uncon_suppression_methods
from contrast_api.data_migration_functionality.errors import SuppressionMethodError
from uncontrast_studies.parsers.uncon_data_parsers import clean_list_from_data


def resolve_uncon_suppression_method(item: dict, index: str):
    suppression_methods_list = []
    main_suppression_methods_data = clean_list_from_data(item["Suppression method Main suppression method"])
    specific_suppression_methods_data = clean_list_from_data(item["Suppression method Specific suppression method"])

    if len(main_suppression_methods_data) == 0:
        raise SuppressionMethodError(f"missing main suppression method, index {index}")

    for main_method in main_suppression_methods_data:
        if main_method in uncon_suppression_methods.keys():
            resolved_main_method = main_method
        else:
            raise SuppressionMethodError(f"invalid main suppression method {main_method}, index {index}")

        if len(uncon_suppression_methods[main_method]) == 0:
            suppression_method = UnconResolvedSuppressionMethodData(main=resolved_main_method, specific=None)
            suppression_methods_list.append(suppression_method)
        else:
            for specific_method in specific_suppression_methods_data:
                if specific_method in uncon_suppression_methods[main_method]:
                    resolved_specific_method = specific_method
                    suppression_method = UnconResolvedSuppressionMethodData(
                        main=resolved_main_method, specific=resolved_specific_method
                    )
                    suppression_methods_list.append(suppression_method)
                else:
                    raise SuppressionMethodError(
                        f"invalid specific suppression method {specific_method}, index {index}"
                    )

    return suppression_methods_list


UnconResolvedSuppressionMethodData = namedtuple("UnconResolvedSuppressionMethodData", ["main", "specific"])
