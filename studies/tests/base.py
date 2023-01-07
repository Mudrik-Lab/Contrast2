from rest_framework.test import APITestCase

from approval_process.choices import ApprovalChoices
from studies.models import Study


class BaseTestCase(APITestCase):
    def given_study_exists(self, **kwargs) -> Study:
        default_study = dict(DOI="10.1016/j.cortex.2017.07.010", title="a study", year=1990,
                             corresponding_author_email="test@example.com",
                             approval_status=ApprovalChoices.APPROVED, key_words=["key", "word"],
                             link="http://dontgohere.com",
                             affiliations="some affiliations", countries=["IL"])
        study_params = {**default_study, **kwargs}
        study, created = Study.objects.get_or_create(**study_params)
        return study
