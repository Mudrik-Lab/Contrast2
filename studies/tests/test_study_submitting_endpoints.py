from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from approval_process.choices import ApprovalChoices
from approval_process.models import ApprovalProcess
from studies.tests.base import BaseTestCase


# Create your tests here.


class SubmittedStudiesViewSetTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_study_creation_by_user(self):
        """
        test study is created with 201
        test approval status is pending and approval process is created
        test submitter gets study back, but other user don't
        """
        self.given_user_exists(username="submitting_user")
        self.given_user_authenticated("submitting_user", "12345")
        self.when_study_created_by_user_via_api()

        res = self.get_pending_studies()
        self.assertEqual(len(res["results"]), 1)

    def when_study_created_by_user_via_api(self, **kwargs):
        default_study = dict(DOI="10.1016/j.cortex.2017.07.010", title="a study", year=1990,
                             corresponding_author_email="test@example.com",
                             authors_key_words=["key", "word"],
                             affiliations="some affiliations", countries=["IL"])
        study_params = {**default_study, **kwargs}

        target_url = reverse("studies-submitted-list")
        res = self.client.post(target_url, data=study_params)
        self.assertEqual(res.status_code, 201)
        return res.data

    def given_user_exists(self, username, password="12345", is_staff=False, is_superuser=False):
        obj = get_user_model().objects.create_user(username=username, password=password, is_staff=is_staff,
                                                   is_superuser=is_superuser)

        return obj

    def given_user_authenticated(self, username, password):
        auth_url = reverse("api-token-obtain-pair")
        res = self.client.post(auth_url, data=dict(username=username, password=password))
        access_token = res.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def get_pending_studies(self):
        target_url = reverse("studies-submitted-list")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, 200)
        return res.data
