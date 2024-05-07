import numpy
import pandas


def get_list_from_excel(path: str, sheet_name: str) -> list:
    read_excel = pandas.read_excel(path, sheet_name=sheet_name)
    nan_removed = read_excel.replace(numpy.nan, "")
    list_from_excel = nan_removed.to_dict("records")

    return list_from_excel


def add_to_notes(prefix, text: str):
    note = f"{prefix} notes: {text}; "
    return note


def find_in_list(items_to_compare: list, compared_items_list: list):
    clean_items_to_compare = [item.split("(")[0].strip() if "(" in item else item.strip() for item in items_to_compare]
    resolved_list = []
    for lookup_item in clean_items_to_compare:
        for item in compared_items_list:
            if item.lower() == lookup_item.lower():
                resolved_list.append(item)

    return resolved_list


def clean_text(text: str):
    cleaned_text = "".join(char for char in text if char.isprintable()).strip()
    return cleaned_text
