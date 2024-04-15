from contrast_api.data_migration_functionality.studies_parsing_helpers import resolve_authors_keywords_from_text, \
    resolve_country_from_affiliation_text, parse_country_names_to_codes, validate_year, \
    resolve_authors_from_authors_text
from studies.models import Study, Author
from studies.parsers.process_row import logger


def create_study(item: dict):
    # parse author keywords and countries from text
    text = item["Author.Keywords"]
    if text:
        author_keywords = resolve_authors_keywords_from_text(text)
    else:
        author_keywords = [""]
    country_names = list(resolve_country_from_affiliation_text(item["Affiliations"]))
    country_codes = parse_country_names_to_codes(country_names)
    year = int(validate_year(item["Year"]))
    funding = str(item["Funding.Details"])

    study, created = Study.objects.get_or_create(
        DOI=item["DOI"],
        title=item["Title"],
        year=year,
        corresponding_author_email="placeholder@email",
        approval_status=1,
        authors_key_words=author_keywords,
        funding=funding,
        source_title=item["Source.Title"],
        abbreviated_source_title=item["Abbreviated.Source.Title"],
        countries=country_codes,
        affiliations=item["Affiliations"],
    )
    # parse authors and add to study
    authors = []
    authors_names = resolve_authors_from_authors_text(item["Authors"])
    for author_name in authors_names:
        author, created = Author.objects.get_or_create(name=author_name)
        authors.append(author)
    for author in authors:
        study.authors.add(author)

    logger.info(f"study {study.DOI} created")
    return study
