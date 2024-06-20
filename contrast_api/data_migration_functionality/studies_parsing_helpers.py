import re
from typing import List

from django_countries import countries


def resolve_authors_from_authors_text(text: str):
    authors_list = text.split(", ")
    authors_list = [author.replace("...", "").replace("_", "").strip() for author in authors_list]
    return authors_list


def resolve_countries(text: str):
    countries_list = text.split(";")
    countries_list = [country.strip() for country in countries_list]
    return countries_list


def resolve_country_from_affiliation_text(text: str):
    affiliations_list = text.split("; ")
    resolved_countries = []
    for affiliation in affiliations_list:
        country = affiliation.split(", ")[-1].strip()
        resolved_countries.append(country)

    set_of_countries = set(resolved_countries)

    return set_of_countries


def resolve_authors_keywords_from_text(text: str):
    authors_keyword_list = text.split(";")
    authors_keyword_list = [author.strip() for author in authors_keyword_list]
    return authors_keyword_list


class ProblemInStudyExistingDataException(Exception):
    pass


def validate_year(text):
    not_a_number = re.search("[a-z]+", str(text))
    empty = re.match("^$", str(text))
    whitespace = re.fullmatch("\s+", str(text))

    if not_a_number or empty or whitespace:
        raise ProblemInStudyExistingDataException()
    else:
        year = int(text)
    return year


class MissingCountryDetectionException(Exception):
    pass


countries_override = {"United States": "United States of America", "England": "United Kingdom"}


def parse_country_names_to_codes(country_names: List[str]) -> List[str]:
    country_codes = []
    for name in country_names:
        name = name.strip()
        code = countries.by_name(name)
        if len(code) == 0:
            if name in countries_override.keys():
                code = countries.by_name(countries_override.get(name))
            elif name == "missing":  # TODO: remove this option after finalizing dataset
                continue
            else:
                raise MissingCountryDetectionException(f"Missing country {name}")
        country_codes.append(code)

    return country_codes


def journal_parser(text: str):
    return text.strip()
