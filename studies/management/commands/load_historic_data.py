from django.core.management import BaseCommand
import pandas
import json

class Command(BaseCommand):
    help = 'Load historic data'

    def handle(self, *args, **options):

        # Read Excel document and convert to JSON-file
        excel_data_df = pandas.read_excel('studies/data/Contrast2_Data_For_Drorsoft.xlsx', sheet_name='sheet1',
                                          index_col=2)
        historic_data_json = excel_data_df.to_json(orient='records')
        historic_data_json_dict = json.loads(historic_data_json)

        with open('historic_data.json', 'w') as json_file:
            json.dump(historic_data_json_dict, json_file)
