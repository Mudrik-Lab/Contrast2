
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





