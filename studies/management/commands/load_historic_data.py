from django.core.management import BaseCommand
import pandas
from configuration.initial_setup import task_types, techniques, paradigms, finding_tag_types
from studies.management.historic_data_helpers import get_paradigms_from_data, get_finding_tag_type_from_data, \
    get_finding_description_from_data

from studies.models import Study, Author, Experiment, Technique, FindingTag, FindingTagFamily, Sample, FindingTagType, \
    TaskType, Task
from studies.studies_parsing_helpers import parse_authors_from_authors_text, parse_authors_keywords_from_text, \
    resolve_country_from_affiliation_text


class Command(BaseCommand):
    help = 'Load historic data'

    def handle(self, *args, **options):

        # Read Excel document and convert to dict
        experiments_data_df = pandas.read_excel('studies/data/Contrast2_Data_For_Drorsoft.xlsx', sheet_name='sheet1')
        studies_data_df = pandas.read_excel('studies/data/Contrast2_Data_For_Drorsoft.xlsx',
                                            sheet_name='Included_Metadata')
        studies_historic_data_list = studies_data_df.to_dict("records")
        historic_data_list = experiments_data_df.to_dict("records")

        # iterate over studies
        for item in studies_historic_data_list:
            author_keywords = parse_authors_keywords_from_text(item["Author.Keywords"])
            countries = resolve_country_from_affiliation_text(item["Affiliations"])

            study = Study.objects.get_or_create(DOI=item["DOI"], title=item["Title"], year=item["Year"],
                                                corresponding_author_email="placeholder@email", approval_status=1,
                                                authors_key_words=author_keywords, funding=item["Funding.Details"],
                                                source_title=item["Source.Title"],
                                                abbreviated_source_title=item["Abbreviated.Source.Title"],
                                                countries=countries, affiliations=item["Affiliations"])
            authors = []
            authors_names = parse_authors_from_authors_text(item["Authors"])
            for author_name in authors_names:
                author = Author.objects.get_or_create(name=author_name)
                authors.append(author)
            for author in authors:
                study.authors.add(author)


        # iterate over experiments
        for item in historic_data_list:
            is_included = bool(item["Should be included? [0 = Not Included, 1 = Included]"])
            if not is_included:
                historic_data_list.remove(item)

            study = Study.objects.get(DOI=item["Paper.DOI"])

            theories = ['GNW', 'IIT', 'HOT', 'RPT']
            theory_driven_theories = []
            theory_driven = ""
            for (key, value) in item.items():
                if "Theory Driven" not in key:
                    continue
                theory_driven = value[0]
                for theory in theories:
                    if theory not in value:
                        continue
                    theory_driven_theories.append(theory)

            findings_ncc_tags = get_finding_description_from_data(item)
            experiment = Experiment.objects.get_or_create(study=study, finding_description=findings_ncc_tags, interpretations,
                                                          type_of_consciousness=item[
                                                              'State - Content [0=State,1=Content,2 = State And Content]'],
                                                          is_reporting=item['Experimental paradigms.Report [0 = No-Report, 1 = Report, 2 = Report And No-Report]'], theory_driven=theory_driven,
                                                          theory_driven_theories=theory_driven_theories, type)
            techniques_in_historic_data = []
            for technique in techniques:
                if technique not in item["Techniques"]:
                    continue
                parsed_technique = Technique.objects.get_or_create(name=technique)
                techniques_in_historic_data.append(parsed_technique)
            for technique in techniques_in_historic_data:
                experiment.techniques.add(technique)

            paradigms_in_data = get_paradigms_from_data(paradigms, item)
            for paradigm in paradigms_in_data:
                experiment.paradigms.add(paradigm)



            sample = Sample.objects.get_or_create(experiment=experiment, type=item["Sample.Type"],total_size=["Sample.Total"],
                                                  size_included=["Sample.Included"])
            coded_task_type = ""
            for (key, value) in item.items():
                if "Task.Code" not in key:
                    continue
                task_code = value[0]
                coded_task_type = task_types[task_code - 1]
            task_type = TaskType.objects.get_or_create(name=coded_task_type)
            task = Task.objects.get_or_create(experiment=experiment, description=item["Task.Description"], type=task_type)



            # TODO: parse the data related to finding_tag in historic_data_helpers
            tag_type_in_data, tag_type_family_in_data = get_finding_tag_type_from_data(finding_tag_types, item)
            tag_family = FindingTagFamily.objects.get_or_create(name=tag_type_family_in_data)
            tag_type = FindingTagType.objects.get_or_create(name=tag_type_in_data, family=tag_family)
            finding_tag = FindingTag.objects.get_or_create(experiment=experiment, type=tag_type, family=tag_family)
