
from contrast_api.tests.base import BaseTestCase
from uncontrast_studies.management.commands.errors_logger import write_errors_to_log


# Create your tests here.


class UnContrastDataMigrationTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_error_logger(self):
        item_1 = {"journal": "invalid journal data", "study_id": "1", "task": "some task", "sample type": "some sample type"}
        item_2 = {"journal": "journal data", "study_id": "missing", "task": "some task", "sample type": "some sample type"}
        item_3 = {"journal": "journal data", "study_id": "2", "task": "invalid task data", "sample type": "some sample type"}
        item_4 = {"journal": "journal data", "study_id": "3", "task": "some task", "sample type": "invalid sample type"}
        logs = {
            "studies_problematic_data_log": [item_1],
            "invalid_study_metadata_log": [item_2],
            "invalid_paradigm_data_log": [],
            "invalid_task_data_log": [item_3],
            "invalid_finding_data_log": [],
            "sample_type_errors_log": [item_4],
            "sample_size_errors_log": []
                }
        test_path = "uncontrast_studies/data/test_errors_log.xlsx"
        res = write_errors_to_log(logs, test_path)
        print(res)
        self.assertEqual(len(res), 4)





