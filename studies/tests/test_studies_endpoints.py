from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


# Create your tests here.
class StudiesViewSetTestCase(APITestCase):
    def setUp(self) -> None:
        super().setUp()

    def tearDown(self) -> None:
        super().tearDown()

    def test_studies_endpoint_is_responding_to_list(self):
        target_url = reverse("studies-list")
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)