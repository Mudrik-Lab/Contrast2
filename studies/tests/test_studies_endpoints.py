from django.urls import reverse
from rest_framework import status

from approval_process.choices import ApprovalChoices
from approval_process.models import ApprovalProcess
from contrast_api.tests.base import BaseTestCase


# Create your tests here.


class StudiesViewSetTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_studies_endpoint_is_responding_to_list_for_approved(self):
        target_url = reverse("studies-list")
        self.given_study_exists(title="test_title")

        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "test_title")

    def test_studies_endpoint_is_not_returning_pending_studies(self):
        target_url = reverse("studies-list")
        self.given_study_exists(title="test_title", approval_status=ApprovalChoices.PENDING)

        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["count"], 0)

        self.given_study_exists(title="better_title", approval_status=ApprovalChoices.APPROVED,
                                                 DOI="10.1017/j.cortex.2017.07.010")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["title"], "better_title")

    def test_studies_endpoint_is_responding_to_list(self):
        target_url = reverse("excluded_studies-list")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_excluded_studies_endpoint_is_not_returning_approved_studies(self):
        target_url = reverse("excluded_studies-list")
        self.given_study_exists(title="test_title", approval_status=ApprovalChoices.APPROVED)

        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["count"], 0)

        self.given_study_exists(title="better_title", approval_status=ApprovalChoices.PENDING,
                                                DOI="10.1017/j.cortex.2017.07.010")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["count"], 0)

        rejected_study = self.given_study_exists(title="rejected_title", approval_status=ApprovalChoices.PENDING,
                                                 DOI="10.1018/j.cortex.2017.07.010")
        self.given_study_rejected_with_reason(rejected_study, "irrelevant")

        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(data["count"], 1)

        self.assertEqual(data["results"][0]["title"], "rejected_title")

    def given_study_rejected_with_reason(self, study, exclusion_reason: str):
        study.approval_process = ApprovalProcess.objects.create(exclusion_reason=exclusion_reason)
        study.approval_status = ApprovalChoices.REJECTED
        study.save()
