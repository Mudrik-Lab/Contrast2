import os
import unittest

from contrast_api.tests.base import BaseTestCase
from uncontrast_studies.services.errors_logger import write_to_log


# Create your tests here.


def test_folder_doesnt_exist():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(current_dir, "data")
    parent_data_dir = os.path.join(current_dir, "../data")

    return not (os.path.exists(data_dir) or os.path.exists(parent_data_dir))


class UnContrastDataMigrationTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    @unittest.skipIf(test_folder_doesnt_exist(), "Skipping if test data folder doesn't exist")
    def test_error_logger(self):
        item_1 = {
            "journal": "invalid journal data",
            "study_id": "1",
            "task": "some task",
            "sample type": "some sample type",
        }
        item_2 = {
            "journal": "journal data",
            "study_id": "missing",
            "task": "some task",
            "sample type": "some sample type",
        }
        item_3 = {
            "journal": "journal data",
            "study_id": "2",
            "task": "invalid task data",
            "sample type": "some sample type",
        }
        item_4 = {"journal": "journal data", "study_id": "3", "task": "some task", "sample type": "invalid sample type"}
        logs = {
            "studies_problematic_data_log": [item_1],
            "invalid_study_metadata_log": [item_2],
            "invalid_paradigm_data_log": [],
            "invalid_task_data_log": [item_3],
            "invalid_finding_data_log": [],
            "sample_type_errors_log": [item_4],
            "sample_size_errors_log": [],
        }
        test_path = "uncontrast_studies/data/test_errors_log.xlsx"
        res = write_to_log(logs, test_path)
        print(res)
        self.assertEqual(len(res), 4)
