from collections import namedtuple
from typing import NamedTuple


def parse_authors_from_authors_text(text: str):
    authors_list = text.split(", ")

    return authors_list


def resolve_country_from_affiliation_text(text: str):
    affiliations_list = text.split("; ")
    countries = []
    for affiliation in affiliations_list:
        country = affiliation.split(", ")[-1].strip()
        countries.append(country)

    set_of_countries = set(countries)

    return set_of_countries


def parse_authors_keywords_from_text(text: str):
    authors_keyword_list = text.split("; ")

    return authors_keyword_list


def find_in_list(lookup_value: str, search_list: list):
    found_item = ""
    for item in search_list:
        if lookup_value.strip().lower() == item.lower():
            found_item = item
    return found_item


TypeFromData = namedtuple("TypeFromData", ["input_type", "input_comment"])


def parse_consciousness_measure_type_from_data(
        text: str):  # TODO: change return type to list of dicts instead of tuples
    ITEM_SEP = '+'
    START_FINDING_SEP = '('
    END_FINDING_SEP = ')'
    LOOKUP_LIST = ["None",
                   "Condition Assessment",
                   "Subjective",
                   "State Induction Assessment",
                   "Sleep Monitoring",
                   "Objective"]

    consciousness_measure_types = text.split(ITEM_SEP)
    consciousness_measure_types_list = []
    for consciousness_measure_type in consciousness_measure_types:
        if START_FINDING_SEP in consciousness_measure_type:
            resolved_type = find_in_list(consciousness_measure_type.split(START_FINDING_SEP)[0], LOOKUP_LIST)
            comment = consciousness_measure_type.split(START_FINDING_SEP)[1].replace(END_FINDING_SEP, '').strip()
        else:
            comment = ''
            resolved_type = (find_in_list(consciousness_measure_type, LOOKUP_LIST))
        type_from_data = TypeFromData(resolved_type, comment)
        consciousness_measure_types_list.append(type_from_data)

    return consciousness_measure_types_list
