from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from approval_process.choices import ApprovalChoices
from studies.models import Study


# Create your tests here.
class StudiesViewSetTestCase(APITestCase):
    def setUp(self) -> None:
        super().setUp()


    def tearDown(self) -> None:
        super().tearDown()

    def test_studies_endpoint_is_responding_to_list_for_approved(self):
        target_url = reverse("studies-list")
        approved_study = self.given_study_exists(title="test_title")

        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "test_title")

    def test_studies_endpoint_is_not_returning_pending_studies(self):
        target_url = reverse("studies-list")
        pending_study = self.given_study_exists(title="test_title", approval_status=ApprovalChoices.PENDING)

        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["count"], 0)

    def given_study_exists(self, **kwargs):
        default_study = dict(DOI="10.1016/j.cortex.2017.07.010", title="a study", year=1990,
                             corresponding_author_email="test@example.com",
                             approval_status=ApprovalChoices.APPROVED, key_words=["key", "word"],
                             link="http://dontgohere.com",
                             affiliations="some affiliations", countries=["IL"])
        study_params = {**default_study, **kwargs}
        study, created = Study.objects.get_or_create(**study_params)
        return study