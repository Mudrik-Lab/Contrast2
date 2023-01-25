from django.core.management import BaseCommand
import pandas
import json

from studies.models import Study, Author, Experiment, Technique
from studies.studies_parsing_helpers import parse_authors_from_authors_text, parse_authors_keywords_from_text, \
    resolve_country_from_affiliation_text


class Command(BaseCommand):
    help = 'Load historic data'

    def handle(self, *args, **options):

        # Read Excel document and convert to JSON-file
        experiments_data_df = pandas.read_excel('studies/data/Contrast2_Data_For_Drorsoft.xlsx', sheet_name='sheet1')
        studies_data_df = pandas.read_excel('studies/data/Contrast2_Data_For_Drorsoft.xlsx',
                                            sheet_name='Included_Metadata')

        studies_historic_data_list = studies_data_df.to_dict("records")
        # iterate over studies
        for item in studies_historic_data_list:
            authors = []
            authors_names = parse_authors_from_authors_text(item["Authors"])
            for author_name in authors_names:
                author = Author.objects.get_or_create(name=author_name)
                authors.append(author)

            author_keywords = parse_authors_keywords_from_text(item["Author.Keywords"])
            countries = resolve_country_from_affiliation_text(item["Affiliations"])

            study = Study.objects.get_or_create(DOI=item["DOI"], title=item["Title"], year=item["Year"],
                                                corresponding_author_email="placeholder@email", approval_status=1,
                                                authors_key_words=author_keywords, funding=item["Funding.Details"],
                                                source_title=item["Source.Title"],
                                                abbreviated_source_title=item["Abbreviated.Source.Title"],
                                                countries=countries, affiliations=item["Affiliations"])
            for author in authors:
                study.authors.add(author)

        historic_data_list = experiments_data_df.to_dict("records")
        # iterate over experiments

