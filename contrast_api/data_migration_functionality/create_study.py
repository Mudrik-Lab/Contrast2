from approval_process.choices import ApprovalChoices
from contrast_api.choices import StudyTypeChoices
from contrast_api.data_migration_functionality.studies_parsing_helpers import (
    resolve_authors_keywords_from_text,
    resolve_country_from_affiliation_text,
    parse_country_names_to_codes,
    validate_year,
    resolve_authors_from_authors_text,
    resolve_countries,
    journal_parser,
)
from studies.models import Study, Author
from studies.parsers.process_row import logger  # TODO: change to shared logger for both sites


def create_study(item: dict, unconsciousness):
    authors = []

    if unconsciousness:
        source_title = journal_parser(item["Journal"])
        country_names = resolve_countries(item["Countries"])
        study_type = StudyTypeChoices.UNCONSCIOUSNESS
        funding = ""
        affiliations = ""
        abbreviated_source_title = journal_parser(item["Journal abbreviated"])
        author_keywords = [""]
        authors_names = resolve_authors_keywords_from_text(item["Authors"])
        for author_name in authors_names:
            author, created = Author.objects.get_or_create(name=author_name)
            authors.append(author)

    else:
        funding = str(item["Funding.Details"])
        country_names = list(resolve_country_from_affiliation_text(item["Affiliations"]))
        source_title = item["Source.Title"]
        affiliations = item["Affiliations"]
        abbreviated_source_title = item["Abbreviated.Source.Title"]
        study_type = StudyTypeChoices.CONSCIOUSNESS

        author_keywords_text = item["Author.Keywords"]
        if author_keywords_text:
            author_keywords = resolve_authors_keywords_from_text(author_keywords_text)
        else:
            author_keywords = [""]

        authors_names = resolve_authors_from_authors_text(item["Authors"])
        for author_name in authors_names:
            author, created = Author.objects.get_or_create(name=author_name)
            authors.append(author)

    DOI = item["DOI"]
    title = item["Title"]
    year = int(validate_year(item["Year"]))
    corresponding_author_email = "placeholder@email"
    approval_status = ApprovalChoices.APPROVED
    country_codes = parse_country_names_to_codes(country_names)

    try:
        study = Study.objects.get(DOI=DOI)
    except Study.DoesNotExist:
        study = Study.objects.create(
            DOI=DOI,
            title=title,
            year=year,
            corresponding_author_email=corresponding_author_email,
            approval_status=approval_status,
            authors_key_words=author_keywords,
            funding=funding,
            source_title=source_title,
            abbreviated_source_title=abbreviated_source_title,
            countries=country_codes,
            affiliations=affiliations,
            type=study_type,
        )
        # add authors to study
        for author in authors:
            study.authors.add(author)

        logger.info(f"study {study.DOI} created")

    return study
